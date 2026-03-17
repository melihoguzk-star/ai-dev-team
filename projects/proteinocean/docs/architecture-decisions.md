# ProteinOcean iOS — Mimari Kararlar

**Tarih:** 2026-03-05
**Agent:** system-architect (retrospektif — mevcut implementasyondan çıkarılmıştır)

---

## 1. PLATFORM SEÇİMİ

**Seçim:** iOS Native (Swift 5.9+ / SwiftUI)

**Gerekçe:**
- proteinocean.com kullanıcı kitlesi premium spor beslenme alıcıları → Apple ekosistemine yakın
- Kapsam sadece görüntüleme (listeleme, filtreleme) → cross-platform overkill
- Native performans ve HIG uyumu öncelikli

**Alternatifler ve Eleme:**
- Flutter: Dart ekibi yok, ek bağımlılık
- React Native: Web ekibi yok, JS bridge overhead

**Risk:** Android kullanıcılar dışarıda kalır. Ancak kapsam bunu kabul ediyor.

---

## 2. MİMARİ PATTERN

**Seçim:** MVVM + @Observable (iOS 17+)

**Gerekçe:**
- Ürün listeleme ve kategori görüntüleme — orta-düşük karmaşıklık
- SwiftUI + @Observable en az boilerplate ile reactive UI
- Dependency injection: `ProductRepositoryProtocol` ile mock/real ayrımı

**Bileşenler:**
```
View → ViewModel (@Observable) → Repository Protocol → GraphQLClient (actor)
```

**Alternatifler:**
- Clean Architecture: Overkill — tek API kaynağı, basit use case
- TCA (The Composable Architecture): Öğrenme eğrisi, gereksiz karmaşıklık

---

## 3. API TASARIMI

**Seçim:** ikas GraphQL API (api.myikas.com/api/v1/admin/graphql)

**Gerekçe:**
- Hazır e-ticaret API — ürün ve kategori endpoint'leri mevcut
- Ayrı backend maliyeti ve geliştirme süresi gereksiz
- GraphQL ile sadece ihtiyaç duyulan alanlar çekilir (network efficiency)

**Auth:** Bearer Token (ikas Private App)
- Token: Environment variable (`IKAS_API_TOKEN`)
- Mock mod: `IkasAPIConfig.useMockData = true`

**Kullanılan Sorgular:**
```graphql
# Kategoriler
query ListCategories { listCategory { data { id name slug imageUrl productCount parentId } count } }

# Ürünler
query ListProducts($filter, $pagination, $sort) {
  listProduct(...) { data { id name imageList variants categories brand } count }
}
```

**Pagination:** offset-based (limit: 24, skip: page * 24)
**Sıralama:** BEST_SELLER | LAST_ADDED | PRICE_ASC | PRICE_DESC

---

## 4. PROJE YAPISI

```
ProteinOcean/
├── App/
│   ├── ProteinOceanApp.swift    → @main giriş noktası
│   └── ContentView.swift        → TabView (Kategoriler | Ürünler)
├── Core/
│   ├── Network/
│   │   ├── GraphQLClient.swift  → URLSession actor, GraphQL executor
│   │   ├── IkasAPIConfig.swift  → Endpoint, token, mock/real switch
│   │   ├── IkasQueries.swift    → GraphQL sorgu string'leri
│   │   ├── ProductRepository.swift     → Gerçek API repository
│   │   └── MockProductRepository.swift → Test/Preview için mock
│   └── Models/
│       ├── Product.swift        → Product, Variant, Price, Stock, Brand, Image
│       └── Category.swift       → StoreCategory
└── Features/
    ├── Categories/
    │   ├── Views/CategoriesView.swift
    │   └── ViewModels/CategoriesViewModel.swift
    └── Products/
        ├── Views/ProductListView.swift  (ProductCard dahil)
        └── ViewModels/ProductListViewModel.swift
```

**Package Manager:** SPM (Package.swift + project.yml/XcodeGen)
**Min OS:** iOS 17.0

---

## 5. NETWORK LAYER

**GraphQLClient (actor):**
- URLSession ile async/await
- Cache policy: `.returnCacheDataElseLoad` (hafif caching)
- Timeout: 30 saniye
- 401 → `NetworkError.unauthorized`
- GraphQL errors → `NetworkError.apiError`

**Repository Pattern:**
- `ProductRepositoryProtocol` — test edilebilirlik için
- `ProductRepository` — gerçek ikas API
- `MockProductRepository` — SwiftUI Preview ve geliştirme

---

## 6. STATE YÖNETİMİ

- `@Observable` + `@State` — iOS 17+ native
- `@MainActor` — tüm ViewModel'lar main thread'de
- Pagination state: `currentPage`, `hasMore`, `isLoadingMore`
- Error state: `errorMessage: String?`

---

## 7. RİSKLER

| Risk | Olasılık | Etki | Çözüm |
|------|----------|------|-------|
| ikas API token süresi dolması | Orta | Yüksek | Hata mesajı göster, admin paneli yönlendirmesi |
| ikas API rate limiting | Düşük | Orta | Cache policy ile istek azaltma |
| Mock data ile prod farkı | Orta | Düşük | Token alındığında gerçek data ile test |
| iOS 17 altı cihaz desteği yok | Yüksek | Düşük | Hedef kitle premium, güncel cihaz kullanır |
