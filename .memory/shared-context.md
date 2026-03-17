# Shared Context — Tüm Agent'lar İçin

Son güncelleme: 2026-03-05

## Proje Bilgileri
- **Platform:** Web → iOS dönüşüm pipeline'ı
- **Hedef:** iOS (Swift/SwiftUI, iOS 17+)
- **Backend:** FastAPI (Python 3.11+)
- **Veritabanı:** SQLite (dev) → PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.0 + Alembic
- **API Stili:** REST, `/api/v1/` prefix, offset pagination
- **iOS Pattern:** MVVM + @Observable
- **iOS Networking:** URLSession + async/await
- **iOS Persistence:** SwiftData
- **iOS Navigation:** TabBar (5 tab) + NavigationStack

## Naming Convention'lar

| Katman | Format | Örnek |
|--------|--------|-------|
| Backend endpoint | kebab-case | `/api/v1/user-profiles` |
| Backend dosya | kebab-case | `user-service.py` |
| Backend sınıf | PascalCase | `UserService` |
| Backend fonksiyon | snake_case | `get_user_by_id()` |
| Veritabanı tablo | snake_case | `user_profiles` |
| Veritabanı sütun | snake_case | `created_at` |
| iOS View | PascalCase + View | `UserProfileView` |
| iOS ViewModel | PascalCase + ViewModel | `UserProfileViewModel` |
| iOS Model | PascalCase | `User`, `Post` |
| iOS dosya | PascalCase | `UserProfileView.swift` |
| iOS protocol | PascalCase + capability | `Cacheable`, `UserFetching` |
| API response key | camelCase | `userId`, `createdAt` |

## Paylaşılan Kararlar
- DEC-001: Backend karmaşıklık düşük (basit CRUD)
- DEC-002: iOS 8-10 ekran tahmini
- DEC-003: Auth yok (güvenlik seviyesi düşük)
- DEC-004–DEC-015: Mimari kararlar (architecture-decisions.md'de detaylı)

## Dosya Yapısı
- Analiz çıktıları: `~/ai-dev-team/analysis/`
- Mimari dokümanlar: `~/ai-dev-team/docs/`
- Backend kod: `~/ai-dev-team/backend/`
- iOS kod: `~/ai-dev-team/ios/`
- Test dosyaları: `~/ai-dev-team/tests/`
- Altyapı: `~/ai-dev-team/infra/`
- Pipeline config: `~/ai-dev-team/pipeline/`

## Bilinen Sorunlar
- JSONPlaceholder'da yazma işlemleri simüle — gerçek backend gerekli
- `/photos` endpoint'i 5000 kayıt döner — client-side pagination gerekli
- via.placeholder.com fotoğraf URL'leri dış bağımlılık — fallback gerekebilir

## Agent'lar Arası Kurallar
- Her agent sadece kendi worktree'sinde çalışır (GIT ISOLATION)
- Develop/main üzerinde doğrudan değişiklik yapılmaz
- Faz çıktıları merge öncesi pre-merge-check'ten geçer
- Kalite skoru 70+ zorunlu (code-reviewer)
