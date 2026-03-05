import Foundation
import Observation

@Observable
final class ProductListViewModel {
    var products: [Product] = []
    var isLoading = false
    var isLoadingMore = false
    var errorMessage: String?
    var currentSort: ProductSortType = .bestSeller
    var hasMore = true

    private var currentPage = 0
    private let pageSize = 24
    private var categoryId: String?
    private let repository: ProductRepositoryProtocol

    init(categoryId: String? = nil, repository: ProductRepositoryProtocol = IkasAPIConfig.makeRepository()) {
        self.categoryId = categoryId
        self.repository = repository
    }

    func setCategoryId(_ id: String?) {
        categoryId = id
        reset()
    }

    func setSort(_ sort: ProductSortType) {
        currentSort = sort
        reset()
    }

    @MainActor
    func loadProducts() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        currentPage = 0
        do {
            let result = try await repository.fetchProducts(
                categoryId: categoryId,
                page: 0,
                sort: currentSort
            )
            products = result.data
            hasMore = result.data.count == pageSize
            currentPage = 1
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    @MainActor
    func loadNextPage() async {
        guard hasMore, !isLoadingMore, !isLoading else { return }
        isLoadingMore = true
        do {
            let result = try await repository.fetchProducts(
                categoryId: categoryId,
                page: currentPage,
                sort: currentSort
            )
            products.append(contentsOf: result.data)
            hasMore = result.data.count == pageSize
            currentPage += 1
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoadingMore = false
    }

    @MainActor
    private func reset() {
        products = []
        currentPage = 0
        hasMore = true
        errorMessage = nil
        Task { await loadProducts() }
    }
}
