import Foundation

struct StoreCategory: Identifiable, Decodable, Hashable {
    let id: String
    let name: String
    let slug: String?
    let imageUrl: String?
    let productCount: Int?
    let parentId: String?

    var isRoot: Bool { parentId == nil }

    enum CodingKeys: String, CodingKey {
        case id, name, slug, imageUrl, productCount, parentId
    }
}

// ikas API listCategory response wrapper
struct ListCategoryData: Decodable {
    let listCategory: CategoryList
}

struct CategoryList: Decodable {
    let data: [StoreCategory]
    let count: Int
}
