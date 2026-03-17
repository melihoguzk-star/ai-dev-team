import XCTest
@testable import ProteinOcean

// AC-001: API başarılı döndüğünde ≥1 kategori grid'de görünür
// AC-002: API hatası durumunda errorMessage set edilir
// BR-001: parentId == nil olan kategoriler root kabul edilir
// FR-005: Sadece root kategoriler listelenir

@MainActor
final class CategoriesViewModelTests: XCTestCase {

    // MARK: - AC-001: Başarılı yükleme

    func test_loadCategories_populatesCategories() async {
        let repo = MockProductRepository()
        let vm = CategoriesViewModel(repository: repo)
        await vm.loadCategories()

        XCTAssertFalse(vm.categories.isEmpty)
        XCTAssertFalse(vm.isLoading)
        XCTAssertNil(vm.errorMessage)
    }

    // MARK: - AC-002: Hata durumu

    func test_loadCategories_setsErrorMessage_onFailure() async {
        let repo = FailingMockRepository()
        let vm = CategoriesViewModel(repository: repo)
        await vm.loadCategories()

        XCTAssertNotNil(vm.errorMessage)
        XCTAssertTrue(vm.categories.isEmpty)
        XCTAssertFalse(vm.isLoading)
    }

    // MARK: - BR-001 + FR-005: rootCategories filtresi

    func test_rootCategories_returnsOnlyParentIdNilCategories() async {
        let repo = MockProductRepository()
        let vm = CategoriesViewModel(repository: repo)
        await vm.loadCategories()

        let roots = vm.rootCategories
        XCTAssertTrue(roots.allSatisfy { $0.parentId == nil })
        // Alt kategoriler (parentId != nil) root'ta görünmemeli
        XCTAssertFalse(roots.contains { $0.parentId != nil })
    }

    // MARK: - subCategories

    func test_subCategories_returnsChildrenOfGivenCategory() async {
        let repo = MockProductRepository()
        let vm = CategoriesViewModel(repository: repo)
        await vm.loadCategories()

        if let protein = vm.categories.first(where: { $0.id == "cat-protein" }) {
            let subs = vm.subCategories(of: protein)
            XCTAssertTrue(subs.allSatisfy { $0.parentId == "cat-protein" })
        }
    }

    // MARK: - Loading state

    func test_isLoading_isFalseAfterCompletion() async {
        let repo = MockProductRepository()
        let vm = CategoriesViewModel(repository: repo)
        await vm.loadCategories()
        XCTAssertFalse(vm.isLoading)
    }
}
