# Python FastAPI Projesi — CI/CD Pipeline

> DevOps mühendisliği çıktısı. GitHub Actions CI workflow, Dockerfile ve docker-compose tanımları.

---

## 1. GitHub Actions CI Workflow

`.github/workflows/ci.yml`

```yaml
# ============================================================
# FastAPI CI Pipeline
# Trigger: push (main, develop) + pull_request (main)
# Jobs : lint → test → build (conditional)
# ============================================================
name: FastAPI CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  DOCKER_IMAGE: ghcr.io/${{ github.repository }}

# --------------------------------------------------------
# Her job birbirinden bağımsız runner üzerinde çalışır.
# "build" job'ı yalnızca main branch push'larında tetiklenir.
# --------------------------------------------------------
jobs:

  # ======================================================
  # JOB 1 — Lint (ruff)
  # ======================================================
  lint:
    name: Lint (ruff)
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip                          # pip bağımlılık cache'i

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff

      - name: Run ruff linter
        run: ruff check . --output-format=github

      - name: Run ruff formatter check
        run: ruff format --check .

  # ======================================================
  # JOB 2 — Test (pytest + coverage)
  # ======================================================
  test:
    name: Test (pytest)
    runs-on: ubuntu-latest
    needs: lint                                # lint başarılı olmalı

    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      ENVIRONMENT: ci

    services:
      # Test sırasında kullanılacak PostgreSQL container
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio httpx

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=app \
            --cov-report=term-missing \
            --cov-report=xml:coverage.xml \
            --junitxml=results.xml \
            -v

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
          retention-days: 14

  # ======================================================
  # JOB 3 — Build (Docker image — sadece main branch)
  # ======================================================
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test                                # test başarılı olmalı
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_IMAGE }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha                 # GitHub Actions cache katmanı
          cache-to: type=gha,mode=max
```

### Workflow Özeti

| Job     | Bağımlılık | Tetiklenme Koşulu          | Açıklama                       |
|---------|------------|----------------------------|--------------------------------|
| `lint`  | —          | Her push & PR              | ruff ile kod kalitesi kontrolü |
| `test`  | `lint`     | Her push & PR              | pytest + coverage raporu       |
| `build` | `test`     | Sadece `main` branch push  | Docker image build & push      |

---

## 2. Dockerfile (Multi-Stage Build)

```dockerfile
# ============================================================
# STAGE 1 — Builder: bağımlılıkları yükle
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Sistem bağımlılıkları (psycopg2 derleme için gerekli)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Önce sadece requirements kopyala → Docker layer cache'ten faydalanılır
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# STAGE 2 — Runtime: minimal imaj
# ============================================================
FROM python:3.11-slim AS runtime

# Güvenlik: root olmayan kullanıcı
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Sadece derlenmiş paketleri kopyala (builder stage'den)
COPY --from=builder /install /usr/local

# Runtime için minimal sistem kütüphanesi
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Uygulama kodunu kopyala
COPY ./app ./app

# Root olmayan kullanıcıya geç
USER appuser

EXPOSE 8000

# Healthcheck: /health endpoint'ine istek at
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Uvicorn ile başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile Mimarisi

```
┌─────────────────────────────────┐
│  STAGE 1: builder               │
│  python:3.11-slim               │
│  ├── gcc, libpq-dev             │
│  └── pip install → /install     │
└──────────────┬──────────────────┘
               │ COPY --from=builder
               ▼
┌─────────────────────────────────┐
│  STAGE 2: runtime               │
│  python:3.11-slim               │
│  ├── libpq5 (sadece runtime)    │
│  ├── /app kodu                  │
│  └── non-root user (appuser)    │
└─────────────────────────────────┘
```

**Multi-stage avantajları:**
- Build araçları (gcc vb.) final imaja dahil edilmez
- Daha küçük imaj boyutu (~150 MB vs ~400 MB)
- Daha az saldırı yüzeyi (güvenlik)

---

## 3. Docker Compose (Local Development)

```yaml
# ============================================================
# docker-compose.yml — Yerel geliştirme ortamı
# Kullanım: docker compose up --build
# ============================================================
services:

  # ----------------------------------------------------------
  # FastAPI uygulama servisi
  # ----------------------------------------------------------
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi-app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db
      - ENVIRONMENT=development
      - DEBUG=true
    volumes:
      - ./app:/app/app                        # Hot-reload için kaynak kodu mount
    depends_on:
      db:
        condition: service_healthy
    command: >
      uvicorn app.main:app
      --host 0.0.0.0
      --port 8000
      --reload
    restart: unless-stopped
    networks:
      - app-network

  # ----------------------------------------------------------
  # PostgreSQL veritabanı servisi
  # ----------------------------------------------------------
  db:
    image: postgres:16-alpine
    container_name: fastapi-db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app_db
    volumes:
      - pgdata:/var/lib/postgresql/data       # Veri kalıcılığı
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

# Named volume: container silinse bile veri korunur
volumes:
  pgdata:

# İzole ağ
networks:
  app-network:
    driver: bridge
```

---

## 4. Kullanılan Cache Stratejileri

| Nerede                  | Cache Türü             | Açıklama                                              |
|-------------------------|------------------------|-------------------------------------------------------|
| `setup-python`          | `cache: pip`           | pip paketlerini runner'da önbelleğe alır              |
| `docker/build-push`     | `cache-from: type=gha` | Docker layer cache'i GitHub Actions üzerinden          |
| `Dockerfile`            | Layer ordering         | `requirements.txt` önce kopyalanır → layer cache       |
| `docker-compose`        | Named volume           | PostgreSQL verisi container restart'larında korunur     |

---

## 5. Güvenlik Notları

- **Non-root user:** Dockerfile'da `appuser` ile çalıştırılır
- **Secrets:** GitHub Actions `secrets.GITHUB_TOKEN` kullanır, hardcoded şifre yok
- **Health check:** Hem Dockerfile hem docker-compose'da tanımlı
- **Minimal base image:** `python:3.11-slim` ile gereksiz paketler çıkarılmış
- **`.dockerignore`** dosyası oluşturulmalı (`.git`, `__pycache__`, `.env`, `tests/` vb.)
