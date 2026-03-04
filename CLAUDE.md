# Project Context

Bu proje **AI Agent Orchestration Platform**'dur — bir web sitesini iOS native uygulamaya dönüştüren 8 fazlı pipeline.

## Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | FastAPI (Python 3.11+) |
| Veritabanı | SQLite (dev) → PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 + Alembic |
| iOS | SwiftUI + MVVM + @Observable |
| iOS Persistence | SwiftData |
| iOS Navigation | TabBar + NavigationStack |
| iOS Min Target | iOS 17+ |
| Package Manager | SPM |

## Pipeline Fazları

1. Web Analiz → `web-analyzer`
2. Mimari Tasarım → `system-architect`
3. BA Doküman → `ba-doc-generator`
4. UI/UX Tasarım → `ui-designer`
5. iOS Dönüşüm → `uiux-translator`
6. Geliştirme → `backend-developer` + `swift-expert` + `mobile-developer`
7. Test & QA → `test-automator` + `code-reviewer`
8. Deploy & Docs → `devops-engineer` + `documentation-engineer`

## Naming Convention'lar

- Backend endpoint: `kebab-case` (`/api/v1/user-profiles`)
- Backend dosya: `kebab-case` (`user-service.py`)
- Backend sınıf: `PascalCase` (`UserService`)
- Backend fonksiyon: `snake_case` (`get_user_by_id`)
- Veritabanı: `snake_case` (`user_profiles`)
- iOS View: `PascalCase` + `View` (`UserProfileView`)
- iOS ViewModel: `PascalCase` + `ViewModel` (`UserProfileViewModel`)
- API response: `camelCase` (`userId`, `createdAt`)

## Git Branching

- `main`: production-ready, squash merge only
- `develop`: entegrasyon, no direct push
- `agent/faz-<N>/<feature>`: faz çalışma branch'i
- `review/<agent>/<tarih>`: kalite inceleme
- `merge/<kaynak>-to-<hedef>`: merge hazırlık

## Dizin Yapısı

```
~/ai-dev-team/
├── analysis/          → Web analiz çıktıları
├── docs/              → Mimari kararlar, BA doküman
├── design/            → UI bileşenleri, tokens.json
├── backend/           → FastAPI kaynak kodu
├── ios/               → SwiftUI iOS projesi
├── tests/             → Test dosyaları
├── infra/             → CI/CD, Docker, Terraform
├── pipeline/          → Pipeline config dosyaları
├── scripts/           → Otomasyon scriptleri
├── .memory/           → Agent hafıza dosyaları
├── .github/           → Branch koruma kuralları
└── worktrees/         → Git worktree'ler (gitignored)
```

## Önemli Kurallar

- Her agent kendi worktree'sinde çalışır (GIT ISOLATION)
- Develop/main üzerinde doğrudan değişiklik yapılmaz
- Kalite skoru ≥ 70 zorunlu (code-reviewer)
- Faz çıktıları pre-merge-check'ten geçmeli
- Yazma işlemleri JSONPlaceholder'da simüle — gerçek backend gerekli
