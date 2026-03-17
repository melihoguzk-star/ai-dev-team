import Foundation

final class MockProductRepository: ProductRepositoryProtocol {

    func fetchCategories() async throws -> [StoreCategory] {
        try await Task.sleep(nanoseconds: 600_000_000) // 0.6s simulated latency
        return MockData.categories
    }

    func fetchProducts(categoryId: String?, page: Int, sort: ProductSortType) async throws -> ProductList {
        try await Task.sleep(nanoseconds: 800_000_000) // 0.8s simulated latency

        var products = categoryId.map { id in
            MockData.products.filter { $0.categories?.contains { $0.id == id } ?? false }
        } ?? MockData.products

        switch sort {
        case .priceAsc:
            products.sort { ($0.minPrice ?? 0) < ($1.minPrice ?? 0) }
        case .priceDesc:
            products.sort { ($0.minPrice ?? 0) > ($1.minPrice ?? 0) }
        case .lastAdded:
            products = products.reversed()
        case .bestSeller:
            break
        }

        let pageSize = 24
        let start = page * pageSize
        let sliced = Array(products.dropFirst(start).prefix(pageSize))
        return ProductList(data: sliced, count: products.count)
    }
}

// MARK: - Mock Data (proteinocean.com'dan gerçekçi veriler)

enum MockData {

    static let categories: [StoreCategory] = [
        StoreCategory(id: "cat-protein", name: "Protein", slug: "protein", imageUrl: nil, productCount: 38, parentId: nil),
        StoreCategory(id: "cat-vitamin", name: "Vitamin", slug: "vitamin", imageUrl: nil, productCount: 52, parentId: nil),
        StoreCategory(id: "cat-spor-gida", name: "Spor Gıdaları", slug: "spor-gidalari", imageUrl: nil, productCount: 41, parentId: nil),
        StoreCategory(id: "cat-saglik", name: "Sağlık", slug: "saglik", imageUrl: nil, productCount: 27, parentId: nil),
        StoreCategory(id: "cat-gida", name: "Gıda", slug: "gida", imageUrl: nil, productCount: 65, parentId: nil),
        StoreCategory(id: "cat-aksesuar", name: "Aksesuar", slug: "aksesuar", imageUrl: nil, productCount: 14, parentId: nil),
        StoreCategory(id: "cat-paket", name: "Paketler", slug: "paketler", imageUrl: nil, productCount: 9, parentId: nil),
        StoreCategory(id: "cat-promosyon", name: "Promosyon", slug: "promosyon", imageUrl: nil, productCount: 22, parentId: nil),
        // Alt kategoriler - Protein
        StoreCategory(id: "cat-whey", name: "Whey Protein", slug: "whey-protein", imageUrl: nil, productCount: 18, parentId: "cat-protein"),
        StoreCategory(id: "cat-collagen", name: "Collagen", slug: "collagen", imageUrl: nil, productCount: 8, parentId: "cat-protein"),
        StoreCategory(id: "cat-amino", name: "Amino Asitler", slug: "amino-asitler", imageUrl: nil, productCount: 12, parentId: "cat-protein"),
    ]

    static let products: [Product] = [
        // Whey Protein ürünleri
        .mock(
            id: "p1",
            name: "ProteinOcean Whey Protein 2280g",
            description: "Yüksek kaliteli whey protein konsantresi. 30g protein / porsiyon.",
            sellPrice: 1249.90, buyPrice: 1549.90,
            stockCount: 45,
            categoryId: "cat-protein", categoryName: "Protein",
            brand: "ProteinOcean",
            variantName: "Çikolata"
        ),
        .mock(
            id: "p2",
            name: "ProteinOcean Whey Protein 908g",
            description: "Kompakt boy whey protein. 24g protein / porsiyon.",
            sellPrice: 649.90, buyPrice: nil,
            stockCount: 120,
            categoryId: "cat-protein", categoryName: "Protein",
            brand: "ProteinOcean",
            variantName: "Vanilya"
        ),
        .mock(
            id: "p3",
            name: "Relentless Hydro Whey 1800g",
            description: "Hidrolize whey protein. Ultra hızlı emilim.",
            sellPrice: 1399.00, buyPrice: 1799.00,
            stockCount: 0,
            categoryId: "cat-protein", categoryName: "Protein",
            brand: "Relentless",
            variantName: "Çilek"
        ),
        .mock(
            id: "p4",
            name: "Flava Collagen Plus 300g",
            description: "Tip 1-2-3 kollajen kompleksi. C vitamini ile güçlendirilmiş.",
            sellPrice: 429.90, buyPrice: 549.90,
            stockCount: 33,
            categoryId: "cat-protein", categoryName: "Protein",
            brand: "Flava",
            variantName: "Portakal"
        ),
        // Vitamin ürünleri
        .mock(
            id: "p5",
            name: "ProteinOcean Vitamin D3 5000 IU 90 Kapsül",
            description: "Yüksek doz D3 vitamini. Bağışıklık sistemi desteği.",
            sellPrice: 189.90, buyPrice: 229.90,
            stockCount: 200,
            categoryId: "cat-vitamin", categoryName: "Vitamin",
            brand: "ProteinOcean",
            variantName: nil
        ),
        .mock(
            id: "p6",
            name: "ProteinOcean Omega 3 1000mg 100 Kapsül",
            description: "Balık yağı kaynaklı Omega 3. EPA + DHA formülü.",
            sellPrice: 259.90, buyPrice: nil,
            stockCount: 88,
            categoryId: "cat-vitamin", categoryName: "Vitamin",
            brand: "ProteinOcean",
            variantName: nil
        ),
        .mock(
            id: "p7",
            name: "ProteinOcean Magnezyum Malat 120 Tablet",
            description: "Yüksek biyoyararlanımlı magnezyum formu.",
            sellPrice: 219.90, buyPrice: 279.90,
            stockCount: 55,
            categoryId: "cat-vitamin", categoryName: "Vitamin",
            brand: "ProteinOcean",
            variantName: nil
        ),
        .mock(
            id: "p8",
            name: "ProteinOcean Zinc 25mg 60 Kapsül",
            description: "Çinko bisglisinat. Bağışıklık ve testosteron desteği.",
            sellPrice: 149.90, buyPrice: nil,
            stockCount: 160,
            categoryId: "cat-vitamin", categoryName: "Vitamin",
            brand: "ProteinOcean",
            variantName: nil
        ),
        // Spor Gıdaları
        .mock(
            id: "p9",
            name: "ProteinOcean BCAA 2:1:1 300g",
            description: "Dallı zincirli amino asitler. Antrenman performansı için.",
            sellPrice: 349.90, buyPrice: 429.90,
            stockCount: 72,
            categoryId: "cat-spor-gida", categoryName: "Spor Gıdaları",
            brand: "ProteinOcean",
            variantName: "Karpuz"
        ),
        .mock(
            id: "p10",
            name: "Relentless Pre-Workout 300g",
            description: "Güçlü pre-workout formülü. Kafein + Beta Alanin.",
            sellPrice: 549.90, buyPrice: 649.90,
            stockCount: 28,
            categoryId: "cat-spor-gida", categoryName: "Spor Gıdaları",
            brand: "Relentless",
            variantName: "Limon"
        ),
        .mock(
            id: "p11",
            name: "ProteinOcean L-Carnitine Sıvı 1000mg 1000ml",
            description: "Sıvı L-Karnitin. Yağ yakımı ve enerji desteği.",
            sellPrice: 399.90, buyPrice: nil,
            stockCount: 41,
            categoryId: "cat-spor-gida", categoryName: "Spor Gıdaları",
            brand: "ProteinOcean",
            variantName: "Kiraz"
        ),
        .mock(
            id: "p12",
            name: "ProteinOcean Kreatin Monohidrat 300g",
            description: "Mikronize kreatin. Güç ve performans artışı.",
            sellPrice: 299.90, buyPrice: 379.90,
            stockCount: 95,
            categoryId: "cat-spor-gida", categoryName: "Spor Gıdaları",
            brand: "ProteinOcean",
            variantName: nil
        ),
        // Gıda
        .mock(
            id: "p13",
            name: "Flava Protein Bar 12'li Kutu",
            description: "20g protein içeren protein bar. Yapay şeker içermez.",
            sellPrice: 479.90, buyPrice: 599.90,
            stockCount: 38,
            categoryId: "cat-gida", categoryName: "Gıda",
            brand: "Flava",
            variantName: "Çikolatalı Fıstık"
        ),
        .mock(
            id: "p14",
            name: "Flava Fıstık Ezmesi 500g",
            description: "Katkısız doğal fıstık ezmesi. Yüksek protein.",
            sellPrice: 219.90, buyPrice: nil,
            stockCount: 67,
            categoryId: "cat-gida", categoryName: "Gıda",
            brand: "Flava",
            variantName: "Sade"
        ),
        // Aksesuar
        .mock(
            id: "p15",
            name: "ProteinOcean Shaker 700ml",
            description: "Sızdırmaz protein shakeri. BPA-free malzeme.",
            sellPrice: 129.90, buyPrice: 159.90,
            stockCount: 110,
            categoryId: "cat-aksesuar", categoryName: "Aksesuar",
            brand: "ProteinOcean",
            variantName: "Siyah"
        ),
        .mock(
            id: "p16",
            name: "ProteinOcean Ölçü Kaşığı Seti",
            description: "4'lü ölçü kaşığı seti. 5g / 10g / 15g / 30g.",
            sellPrice: 49.90, buyPrice: nil,
            stockCount: 200,
            categoryId: "cat-aksesuar", categoryName: "Aksesuar",
            brand: "ProteinOcean",
            variantName: nil
        ),
    ]
}

// MARK: - Product Mock Factory

private extension Product {
    static func mock(
        id: String,
        name: String,
        description: String,
        sellPrice: Double,
        buyPrice: Double?,
        stockCount: Int,
        categoryId: String,
        categoryName: String,
        brand: String,
        variantName: String?
    ) -> Product {
        Product(
            id: id,
            name: name,
            description: description,
            variants: [
                ProductVariant(
                    id: "\(id)-v1",
                    name: variantName,
                    price: VariantPrice(sellPrice: sellPrice, buyPrice: buyPrice, discountPrice: nil),
                    stock: VariantStock(stockCount: stockCount),
                    mainImageId: nil
                )
            ],
            categories: [ProductCategory(id: categoryId, name: categoryName)],
            brand: Brand(id: "brand-\(brand.lowercased())", name: brand),
            imageList: nil
        )
    }
}
