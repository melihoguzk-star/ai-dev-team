import Foundation

protocol ProductRepositoryProtocol {
    func fetchCategories() async throws -> [StoreCategory]
    func fetchProducts(categoryId: String?, page: Int, sort: ProductSortType) async throws -> ProductList
}

final class ProductRepository: ProductRepositoryProtocol {
    private let client = GraphQLClient.shared

    func fetchCategories() async throws -> [StoreCategory] {
        let request = GraphQLRequest(query: IkasQueries.listCategories)
        let response = try await client.execute(request, as: ListCategoryData.self)
        return response.listCategory.data
    }

    func fetchProducts(
        categoryId: String? = nil,
        page: Int = 0,
        sort: ProductSortType = .bestSeller
    ) async throws -> ProductList {
        let query = IkasQueries.listProducts(categoryId: categoryId, page: page, sortBy: sort)
        let request = GraphQLRequest(query: query)
        let response = try await client.execute(request, as: ListProductData.self)
        return response.listProduct
    }
}
