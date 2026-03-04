# Mimari Kararlar — JSONPlaceholder iOS Uygulaması

**Kaynak:** `~/ai-dev-team/pilot-test/analysis/web-analysis-report.html`
**Tarih:** 5 Mart 2026
**Agent:** system-architect (Faz 2)

---

## 1. BACKEND TEKNOLOJİ SEÇİMİ

### Seçim: FastAPI (Python)

**Gerekçe:**
- Site zaten basit REST API sunuyor (6 kaynak, CRUD). JSONPlaceholder sahte API — gerçek bir backend yazılması gerekiyor.
- FastAPI'nin async desteği, otomatik OpenAPI/Swagger dokümantasyonu ve Pydantic model validation'ı bu proje için ideal.
- Proje karmaşıklığı düşük (DEC-001) — overengineering yapılmamalı.

**Neden diğerleri değil:**
| Alternatif | Ret Gerekçesi |
|------------|---------------|
| Express.js (Node) | Geçerli bir alternatif, ancak FastAPI'nin type safety ve otomatik dokümantasyonu üstün |
| Django REST | Bu proje için fazla ağır. Admin panel ve ORM overhead gereksiz |
| Go (Gin/Echo) | Compile step gereksiz karmaşıklık ekler. Bu basitlikte Python yeterli |

**Riskler:** Python performansı yüksek trafik senaryolarında sorun olabilir. Ancak bu bir test projesi — risk ihmal edilebilir.

### Veritabanı: SQLite (development) → PostgreSQL (production)

**Gerekçe:**
- 6 entity, toplam ~6000 kayıt — SQLite development için fazlasıyla yeterli
- PostgreSQL production'da tutarlılık ve ölçeklenebilirlik için
- Basit ilişkisel yapı (1:N) — SQL doğal çözüm

**Neden MongoDB değil:** Veri modeli tamamen ilişkisel (userId → posts, postId → comments). NoSQL gereksiz.

### ORM: SQLAlchemy 2.0 + Alembic

**Gerekçe:**
- FastAPI ile doğal uyum
- SQLAlchemy 2.0'ın yeni async session desteği
- Alembic ile migration yönetimi

### Authentication: Yok (API Key opsiyonel)

**Gerekçe:**
- Orijinal API'de auth yok (DEC-003: güvenlik seviyesi düşük)
- İsteğe bağlı API key header'ı eklenebilir ama gerekli değil
- Pilot test için auth atlanabilir

### Hosting: Railway veya Fly.io

**Gerekçe:**
- Basit deploy (git push), ücretsiz tier mevcut
- FastAPI + PostgreSQL desteği native
- Bu proje için AWS/GCP overengineering olur

---

## 2. API TASARIMI

### Seçim: REST API

**Gerekçe:**
- Orijinal API zaten REST — uyumluluk
- 6 kaynak, basit CRUD — GraphQL overengineering olur
- iOS URLSession + Codable ile REST doğal uyumlu

**Neden GraphQL değil:** Tek bir kaynak tipi bile nested query gerektirmiyor. Over-fetching sorunu yok çünkü response'lar zaten küçük.

### API Versiyonlama: URL prefix

```
/api/v1/posts
/api/v1/users
```

**Gerekçe:** Basit, açık, her HTTP client ile uyumlu.

### Endpoint Yapısı

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/v1/{resource}` | Liste (query params ile filtreleme) |
| GET | `/api/v1/{resource}/{id}` | Detay |
| POST | `/api/v1/{resource}` | Oluştur |
| PUT | `/api/v1/{resource}/{id}` | Güncelle (tam) |
| PATCH | `/api/v1/{resource}/{id}` | Güncelle (kısmi) |
| DELETE | `/api/v1/{resource}/{id}` | Sil |
| GET | `/api/v1/{resource}/{id}/{nested}` | Nested liste |

**Kaynaklar:** `posts`, `comments`, `albums`, `photos`, `todos`, `users`
**Nested route'lar:** Orijinal API ile aynı (posts/comments, albums/photos, users/albums|todos|posts)

### Request/Response Formatı

```json
// Başarılı liste response
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}

// Başarılı tekil response
{
  "data": { ... }
}

// Hata response
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Post bulunamadı",
    "status": 404
  }
}
```

### Error Response Standardı

| Status | Code | Kullanım |
|--------|------|----------|
| 400 | `VALIDATION_ERROR` | Geçersiz request body |
| 404 | `NOT_FOUND` | Kaynak bulunamadı |
| 422 | `UNPROCESSABLE_ENTITY` | Mantıksal hata |
| 500 | `INTERNAL_ERROR` | Sunucu hatası |

### Pagination Stratejisi

```
GET /api/v1/posts?page=1&per_page=20
```

**Gerekçe:** Orijinal API'de pagination yok ama /photos 5000 kayıt döner (Risk #2). Offset-based pagination basit ve yeterli.

---

## 3. VERİTABANI ŞEMASI

### Tablolar

```sql
-- users tablosu
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    website TEXT,
    -- address nested object → ayrı sütunlar
    address_street TEXT,
    address_suite TEXT,
    address_city TEXT,
    address_zipcode TEXT,
    address_geo_lat REAL,
    address_geo_lng REAL,
    -- company nested object → ayrı sütunlar
    company_name TEXT,
    company_catch_phrase TEXT,
    company_bs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts tablosu
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- comments tablosu
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- albums tablosu
CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- photos tablosu
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- todos tablosu
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### İlişkiler

| İlişki | Tip | FK | Cascade |
|--------|-----|-----|---------|
| User → Posts | 1:N | posts.user_id | CASCADE |
| User → Albums | 1:N | albums.user_id | CASCADE |
| User → Todos | 1:N | todos.user_id | CASCADE |
| Post → Comments | 1:N | comments.post_id | CASCADE |
| Album → Photos | 1:N | photos.album_id | CASCADE |

### Index Stratejisi

```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_albums_user_id ON albums(user_id);
CREATE INDEX idx_photos_album_id ON photos(album_id);
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_completed ON todos(user_id, completed);
```

**Gerekçe:** Tüm FK sütunlarında index — nested route sorguları ve filtreleme için. `todos` tablosunda completed filtresi sık kullanılacağı için bileşik index.

### Migration Planı

1. `alembic init` ile migration altyapısı
2. İlk migration: tüm tabloları oluştur
3. Seed migration: JSONPlaceholder'dan çekilen verilerle doldur

---

## 4. iOS MİMARİ KARARLARI

### Mimari Pattern: MVVM

**Gerekçe:**
- SwiftUI ile doğal uyum (@Observable macro)
- Bu proje boyutunda MVVM yeterli — VIPER/Clean Architecture overengineering olur
- View ↔ ViewModel ↔ Repository ↔ NetworkService katmanlı yapı

### Networking Layer: URLSession + async/await

**Gerekçe:**
- iOS 17+ hedef — native async/await tam destek
- 3rd party kütüphane (Alamofire) gereksiz — basit REST API
- Generic `APIClient` sınıfı yeterli

```swift
// Taslak
actor APIClient {
    let baseURL = URL(string: "https://api.example.com/api/v1")!
    
    func fetch<T: Decodable>(_ endpoint: String) async throws -> T {
        let url = baseURL.appending(path: endpoint)
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

### State Management: @Observable (Observation framework)

**Gerekçe:**
- iOS 17+ — @Observable macro kullanılabilir
- @ObservableObject + @Published'dan daha temiz syntax
- SwiftUI view'ları otomatik güncellenir

### Persistence: SwiftData

**Gerekçe:**
- iOS 17+ hedef — SwiftData native ve modern
- Core Data'ya göre çok daha az boilerplate
- Offline cache için ideal (API verisini local'de tut)
- 6 model, basit ilişkiler — SwiftData rahatça karşılar

**Neden Core Data değil:** iOS 17+ hedefle SwiftData tercih edilmeli. Core Data sadece iOS 16 desteği gerekirse.

### Navigation: NavigationStack

**Gerekçe:**
- iOS 17+ — NavigationStack tam destekli
- Deep linking desteği (Navigatable protocol ile)
- TabBar (5 tab) + her tab'da NavigationStack

### Package Manager: SPM (Swift Package Manager)

**Gerekçe:** Xcode native. CocoaPods gereksiz karmaşıklık.

### Minimum iOS Hedef: iOS 17+

**Gerekçe:** SwiftData, @Observable, NavigationStack — hepsi iOS 17 gerektiriyor. Pilot test projesi için en yeni teknolojiler kullanılabilir.

---

## 5. PROJE YAPISI

### Backend Dizin Yapısı

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, router'ları mount et
│   ├── config.py             # Settings (env variables)
│   ├── database.py           # SQLAlchemy engine + session
│   ├── models/               # SQLAlchemy modelleri
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── album.py
│   │   ├── photo.py
│   │   └── todo.py
│   ├── schemas/              # Pydantic request/response şemaları
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── album.py
│   │   ├── photo.py
│   │   └── todo.py
│   ├── routers/              # API endpoint'leri
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   ├── comments.py
│   │   ├── albums.py
│   │   ├── photos.py
│   │   └── todos.py
│   └── seed.py               # JSONPlaceholder verisiyle DB'yi doldur
├── alembic/                  # Migration dosyaları
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── README.md
```

### iOS Proje Dizin Yapısı (Feature-Based)

```
ios/
├── JSONPlaceholder/
│   ├── App/
│   │   ├── JSONPlaceholderApp.swift    # @main entry point
│   │   └── ContentView.swift          # TabBar root view
│   ├── Core/
│   │   ├── Network/
│   │   │   ├── APIClient.swift        # Generic API client
│   │   │   ├── APIEndpoint.swift      # Endpoint enum
│   │   │   └── APIError.swift         # Error types
│   │   ├── Models/                    # Shared Codable models
│   │   │   ├── User.swift
│   │   │   ├── Post.swift
│   │   │   ├── Comment.swift
│   │   │   ├── Album.swift
│   │   │   ├── Photo.swift
│   │   │   └── Todo.swift
│   │   ├── Persistence/
│   │   │   └── SwiftDataModels.swift  # SwiftData @Model'ler
│   │   └── Extensions/
│   │       └── View+Extensions.swift
│   ├── Features/
│   │   ├── Posts/
│   │   │   ├── PostListView.swift
│   │   │   ├── PostDetailView.swift
│   │   │   └── PostViewModel.swift
│   │   ├── Users/
│   │   │   ├── UserListView.swift
│   │   │   ├── UserDetailView.swift
│   │   │   └── UserViewModel.swift
│   │   ├── Albums/
│   │   │   ├── AlbumListView.swift
│   │   │   ├── AlbumDetailView.swift  # Photo grid
│   │   │   └── AlbumViewModel.swift
│   │   ├── Todos/
│   │   │   ├── TodoListView.swift
│   │   │   └── TodoViewModel.swift
│   │   └── Profile/
│   │       └── ProfileView.swift
│   └── Resources/
│       └── Assets.xcassets
├── JSONPlaceholderTests/
└── JSONPlaceholder.xcodeproj
```

### Shared Types / Contracts

Backend Pydantic şemaları ile iOS Codable struct'ları birebir eşleşmeli:

| Backend (Pydantic) | iOS (Codable) | Alanlar |
|--------------------|---------------|---------|
| `PostResponse` | `Post` | id, userId, title, body |
| `UserResponse` | `User` | id, name, username, email, address, phone, website, company |
| `CommentResponse` | `Comment` | id, postId, name, email, body |
| `AlbumResponse` | `Album` | id, userId, title |
| `PhotoResponse` | `Photo` | id, albumId, title, url, thumbnailUrl |
| `TodoResponse` | `Todo` | id, userId, title, completed |

---

## KARAR ÖZETİ

| # | Alan | Seçim | Karmaşıklık |
|---|------|-------|-------------|
| 1 | Backend Framework | FastAPI (Python) | Düşük |
| 2 | Veritabanı | SQLite → PostgreSQL | Düşük |
| 3 | ORM | SQLAlchemy 2.0 + Alembic | Düşük |
| 4 | Auth | Yok | — |
| 5 | Hosting | Railway / Fly.io | Düşük |
| 6 | API Stili | REST + Pagination | Düşük |
| 7 | iOS Pattern | MVVM (@Observable) | Düşük |
| 8 | iOS Network | URLSession + async/await | Düşük |
| 9 | iOS Persistence | SwiftData | Düşük |
| 10 | iOS Navigation | TabBar + NavigationStack | Düşük |
| 11 | iOS Min Target | iOS 17+ | — |
| 12 | Package Manager | SPM | — |
