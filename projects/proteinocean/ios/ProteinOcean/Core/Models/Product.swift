import Foundation

struct Product: Identifiable, Decodable, Hashable {
    let id: String
    let name: String
    let description: String?
    let variants: [ProductVariant]
    let categories: [ProductCategory]?
    let brand: Brand?
    let imageList: [ProductImage]?

    var mainImage: ProductImage? { imageList?.first }
    var baseVariant: ProductVariant? { variants.first }

    var minPrice: Double? {
        variants.compactMap { $0.price?.sellPrice }.min()
    }

    var maxPrice: Double? {
        variants.compactMap { $0.price?.sellPrice }.max()
    }

    var originalPrice: Double? {
        variants.compactMap { $0.price?.buyPrice }.first
    }

    var discountPercent: Int? {
        guard let sell = minPrice, let original = originalPrice, original > sell else { return nil }
        return Int(((original - sell) / original) * 100)
    }

    var isInStock: Bool {
        variants.contains { ($0.stock?.stockCount ?? 0) > 0 }
    }

    enum CodingKeys: String, CodingKey {
        case id, name, description, variants, categories, brand, imageList
    }
}

struct ProductVariant: Decodable, Hashable {
    let id: String
    let name: String?
    let price: VariantPrice?
    let stock: VariantStock?
    let mainImageId: String?
}

struct VariantPrice: Decodable, Hashable {
    let sellPrice: Double
    let buyPrice: Double?
    let discountPrice: Double?
}

struct VariantStock: Decodable, Hashable {
    let stockCount: Int?
}

struct ProductCategory: Decodable, Hashable {
    let id: String
    let name: String
}

struct Brand: Decodable, Hashable {
    let id: String
    let name: String
}

struct ProductImage: Decodable, Hashable {
    let id: String
    let fileName: String?
    let isMain: Bool?

    var cdnUrl: String? {
        guard let fileName else { return nil }
        return "https://cdn.myikas.com/images/\(fileName)"
    }
}

// ikas API listProduct response wrapper
struct ListProductData: Decodable {
    let listProduct: ProductList
}

struct ProductList: Decodable {
    let data: [Product]
    let count: Int
}
