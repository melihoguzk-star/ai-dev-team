# ProteinOcean iOS Kurulum Rehberi

## 1. ikas API Token Alma

1. https://proteinocean.myikas.com/admin adresine gidin
2. **Ayarlar → Geliştirici → Private Apps** sekmesine gidin
3. "Yeni Private App" olusturun:
   - Ad: ProteinOcean Mobile
   - Scopes: Product View, Category View
4. Olusturulan **Access Token**'i kopyalayin

## 2. Xcode Projesi Olusturma

```bash
# iOS dizinine gidin
cd ~/ai-dev-team/projects/proteinocean/ios

# Xcode'da aç (SPM ile)
open Package.swift
```

Xcode'da:
1. Product → Destination → iPhone 15 Pro (iOS 17+) seçin
2. Product → Scheme → ProteinOcean seçin

## 3. API Token'ı Ayarlama

Xcode'da:
1. Product → Scheme → Edit Scheme → Run → Arguments
2. "Environment Variables" bölümüne ekleyin:
   - Key: `IKAS_API_TOKEN`
   - Value: `<aldığınız token>`

Alternatif olarak `IkasAPIConfig.swift` içinde direkt atama:
```swift
static var bearerToken: String { "YOUR_TOKEN_HERE" }
```

## 4. Çalıştırma

Xcode'da Cmd+R ile simulator'da çalıştırın.

## Proje Yapısı

```
ProteinOcean/
├── App/
│   ├── ProteinOceanApp.swift    # @main giriş noktası
│   └── ContentView.swift        # TabBar yapısı
├── Core/
│   ├── Network/
│   │   ├── IkasAPIConfig.swift  # Endpoint + token konfigürasyonu
│   │   ├── GraphQLClient.swift  # ikas GraphQL istemcisi
│   │   ├── IkasQueries.swift    # GraphQL sorguları
│   │   └── ProductRepository.swift # Repository pattern
│   └── Models/
│       ├── Category.swift       # StoreCategory modeli
│       └── Product.swift        # Product + Variant modelleri
└── Features/
    ├── Categories/
    │   ├── Views/CategoriesView.swift      # Kategori grid ekranı
    │   └── ViewModels/CategoriesViewModel.swift
    └── Products/
        ├── Views/ProductListView.swift     # Ürün liste + grid ekranı
        └── ViewModels/ProductListViewModel.swift
```

## ikas API Endpoint Referans

```
GraphQL: https://api.myikas.com/api/v1/admin/graphql
Auth:    Bearer <token>
```

### Kategori Sorgusu
```graphql
query ListCategories {
  listCategory {
    data { id name slug imageUrl productCount parentId }
    count
  }
}
```

### Ürün Sorgusu (Kategoriye Göre)
```graphql
query ListProducts {
  listProduct(
    pagination: { limit: 24, skip: 0 }
    sort: { type: BEST_SELLER }
    filter: { categoryIds: ["CATEGORY_ID"] }
  ) {
    data {
      id name
      imageList { id fileName isMain }
      variants { id price { sellPrice buyPrice } stock { stockCount } }
      categories { id name }
      brand { id name }
    }
    count
  }
}
```
