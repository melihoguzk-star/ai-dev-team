import Foundation
import Observation

@Observable
final class CategoriesViewModel {
    var categories: [StoreCategory] = []
    var isLoading = false
    var errorMessage: String?
    var selectedStoreCategory: StoreCategory?

    private let repository: ProductRepositoryProtocol

    init(repository: ProductRepositoryProtocol = ProductRepository()) {
        self.repository = repository
    }

    var rootCategories: [StoreCategory] {
        categories.filter { $0.isRoot }
    }

    func subCategories(of category: StoreCategory) -> [StoreCategory] {
        categories.filter { $0.parentId == category.id }
    }

    @MainActor
    func loadCategories() async {
        isLoading = true
        errorMessage = nil
        do {
            categories = try await repository.fetchCategories()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}
