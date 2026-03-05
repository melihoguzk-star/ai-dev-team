import Foundation
import Observation

@Observable
@MainActor
final class CategoriesViewModel {
    var categories: [StoreCategory] = []
    var isLoading = false
    var errorMessage: String?
    var selectedStoreCategory: StoreCategory?

    private let repository: ProductRepositoryProtocol

    init(repository: ProductRepositoryProtocol = IkasAPIConfig.makeRepository()) {
        self.repository = repository
    }

    var rootCategories: [StoreCategory] {
        categories.filter { $0.isRoot }
    }

    func subCategories(of category: StoreCategory) -> [StoreCategory] {
        categories.filter { $0.parentId == category.id }
    }

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
