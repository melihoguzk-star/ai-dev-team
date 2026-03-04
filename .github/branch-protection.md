# Branch Koruma Kuralları ve Strateji

## Branch Yapısı

```
main ────────────────────────────────────────────────► production-ready
  │
  └── develop ───────────────────────────────────────► entegrasyon
        │
        ├── agent/faz-1/web-analysis ────────────────► faz çalışması
        ├── agent/faz-2/architecture ────────────────►
        ├── agent/faz-3/ba-document ─────────────────►
        ├── agent/faz-6/backend-api ─────────────────►
        ├── agent/faz-6/ios-core ────────────────────►
        ├── agent/faz-6/ios-ui ──────────────────────►
        │
        ├── review/code-reviewer/2026-03-05 ─────────► kalite inceleme
        │
        └── merge/faz-3-to-develop ──────────────────► merge PR
```

---

## Koruma Kuralları

### `main` Branch

| Kural | Değer |
|-------|-------|
| Doğrudan push | ❌ Yasak |
| Force push | ❌ Yasak |
| Silme | ❌ Yasak |
| Merge yöntemi | PR (Pull Request) zorunlu |
| PR onayı | Minimum 1 onay gerekli |
| Durum kontrolleri | Tüm testler geçmeli |
| Branch kaynağı | Sadece `develop` → `main` merge edilebilir |
| Merge tipi | Squash merge tercih |

### `develop` Branch

| Kural | Değer |
|-------|-------|
| Doğrudan push | ❌ Yasak |
| Force push | ❌ Yasak |
| Silme | ❌ Yasak |
| Merge yöntemi | PR (Pull Request) zorunlu |
| PR onayı | code-reviewer agent kalite skoru ≥ 70 |
| Durum kontrolleri | Lint + unit testler geçmeli |
| Branch kaynağı | `agent/*`, `review/*` veya `merge/*` branch'lerinden |
| Merge tipi | Merge commit (geçmişi koru) |

### Feature Branch'ler (`agent/*`, `review/*`, `merge/*`)

| Kural | Değer |
|-------|-------|
| Doğrudan push | ✅ İzinli |
| Force push | ✅ İzinli (kendi branch'inde) |
| Silme | ✅ Merge sonrası otomatik sil |
| Merge hedefi | `develop` |

---

## Branch Naming Convention

### `agent/<faz-no>/<feature>`

Pipeline fazlarında agent'ların çalışma branch'i.

```
agent/faz-1/web-analysis
agent/faz-2/architecture
agent/faz-3/ba-document
agent/faz-4/ui-design
agent/faz-5/ios-translation
agent/faz-6/backend-api
agent/faz-6/ios-core
agent/faz-6/ios-ui
agent/faz-7/tests
agent/faz-8/deployment
agent/faz-8/documentation
```

**Kurallar:**
- Faz numarası zorunlu
- Feature kısmı kebab-case
- Bir agent tek branch'te çalışır
- Faz tamamlandığında `develop`'a merge edilir

### `review/<agent>/<tarih>`

Code review ve kalite kontrol branch'i.

```
review/code-reviewer/2026-03-05
review/test-automator/2026-03-05
review/prompt-engineer/2026-03-06
```

**Kurallar:**
- Review raporları bu branch'te commit edilir
- Kalite kapısı geçildikten sonra `develop`'a merge

### `merge/<kaynak>-to-<hedef>`

Büyük merge işlemleri için hazırlık branch'i.

```
merge/faz-3-to-develop
merge/develop-to-main
merge/faz-6-backend-to-develop
```

**Kurallar:**
- Conflict resolution bu branch'te yapılır
- Merge hazır olduğunda PR açılır

---

## Git Workflow

### Faz Çalışma Akışı

```bash
# 1. Faz branch'i oluştur
git checkout develop
git pull origin develop
git checkout -b agent/faz-3/ba-document

# 2. Agent çalışır, dosyalar oluşturur
# ... agent çalışması ...

# 3. Commit
git add -A
git commit -m "Faz 3: BA dokümanı oluşturuldu

Agent: ba-doc-generator
Kalite skoru: 82/100
Üretilen dosyalar:
- docs/ba-document.md (45 KB)
"

# 4. Develop'a merge et
git checkout develop
git merge --no-ff agent/faz-3/ba-document -m "Merge faz-3/ba-document into develop"
git branch -d agent/faz-3/ba-document
```

### Release Akışı (Tüm Fazlar Tamamlandığında)

```bash
# 1. Develop'dan main'e merge
git checkout main
git merge --squash develop -m "Release: JSONPlaceholder iOS App v1.0

Pipeline tamamlandı:
- 8 faz, 15 karar, 0 kritik hata
- Backend: FastAPI + PostgreSQL
- iOS: SwiftUI + MVVM + SwiftData
"

# 2. Tag
git tag -a v1.0 -m "İlk release"
```

### Commit Mesaj Formatı

```
Faz <N>: <kısa açıklama>

Agent: <agent-adı>
Kalite skoru: <skor>/100
Üretilen dosyalar:
- <dosya-yolu> (<boyut>)

[Opsiyonel: Kararlar]
- DEC-XXX: <karar açıklaması>
```

---

## GitHub Actions ile Otomasyon (Opsiyonel)

Bu kuralları GitHub'a push ettikten sonra uygulamak için:

1. **Repository Settings → Branches → Branch protection rules**
   - `main`: Require PR, require review, require status checks
   - `develop`: Require PR, require status checks

2. **`.github/workflows/ci.yml`** dosyası ile:
   - PR açıldığında lint + test çalıştır
   - Merge öncesi kalite kontrolü

> **Not:** Bu kurallar local git'te enforce edilemez. GitHub/GitLab'a push edildikten sonra platform settings'ten aktif edilmeli.
