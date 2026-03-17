import Foundation

enum IkasQueries {

    static let listCategories = """
    query ListCategories {
      listCategory {
        data {
          id
          name
          slug
          imageUrl
          productCount
          parentId
        }
        count
      }
    }
    """

    static func listProducts(
        categoryId: String? = nil,
        page: Int = 0,
        limit: Int = 24,
        sortBy: ProductSortType = .bestSeller
    ) -> String {
        let categoryFilter = categoryId.map { """
        , filter: { categoryIds: ["\($0)"] }
        """ } ?? ""

        return """
        query ListProducts {
          listProduct(
            pagination: { limit: \(limit), skip: \(page * limit) }
            sort: { type: \(sortBy.rawValue) }
            \(categoryFilter)
          ) {
            data {
              id
              name
              description
              imageList {
                id
                fileName
                isMain
              }
              variants {
                id
                name
                price {
                  sellPrice
                  buyPrice
                  discountPrice
                }
                stock {
                  stockCount
                }
              }
              categories {
                id
                name
              }
              brand {
                id
                name
              }
            }
            count
          }
        }
        """
    }
}

enum ProductSortType: String {
    case bestSeller = "BEST_SELLER"
    case lastAdded = "LAST_ADDED"
    case priceAsc = "PRICE_ASC"
    case priceDesc = "PRICE_DESC"

    var displayName: String {
        switch self {
        case .bestSeller: return "En Cok Satan"
        case .lastAdded: return "En Yeni"
        case .priceAsc: return "Fiyat: Dusukten Yukseğe"
        case .priceDesc: return "Fiyat: Yuksekten Dusuge"
        }
    }

    static var allCases: [ProductSortType] {
        [.bestSeller, .lastAdded, .priceAsc, .priceDesc]
    }
}
