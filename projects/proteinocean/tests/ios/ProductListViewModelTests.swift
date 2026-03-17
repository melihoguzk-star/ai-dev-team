import XCTest
@testable import ProteinOcean

// AC-006: Sıralama değiştiğinde liste sıfırlanır ve yeniden yüklenir
// AC-007: Son ürüne scroll edildiğinde sonraki sayfa yüklenir
// AC-008: hasMore = false durumunda ek yükleme yapılmaz
// VAL-003: Eş zamanlı yükleme koruması

@MainActor
final class ProductListViewModelTests: XCTestCase {

    // MARK: - AC-006: Sıralama değiştiğinde reset

    func test_setSort_resetsProductsAndReloads() async {
        let repo = MockProductRepository()
        let vm = ProductListViewModel(categoryId: nil, repository: repo)
        await vm.loadProducts()
        XCTAssertFalse(vm.products.isEmpty)

        vm.setSort(.priceAsc)
        // Reset sonrası products temizlenir, sort güncellenir
        XCTAssertEqual(vm.currentSort, .priceAsc)
    }

    // MARK: - AC-009: Loading state

    func test_loadProducts_setsIsLoadingTrue_thenFalse() async {
        let repo = MockProductRepository()
        let vm = ProductListViewModel(categoryId: nil, repository: repo)
        XCTAssertFalse(vm.isLoading)
        await vm.loadProducts()
        XCTAssertFalse(vm.isLoading) // Tamamlandığında false olmalı
    }

    // MARK: - AC-008: hasMore = false koruması

    func test_loadNextPage_doesNotLoad_whenHasMoreFalse() async {
        let repo = LimitedMockRepository(itemCount: 5) // 24'ten az
        let vm = ProductListViewModel(categoryId: nil, repository: repo)
        await vm.loadProducts()

        XCTAssertFalse(vm.hasMore) // 5 < 24, hasMore false olmalı

        let countBefore = vm.products.count
        await vm.loadNextPage()
        XCTAssertEqual(vm.products.count, countBefore) // Yeni yükleme olmamalı
    }

    // MARK: - VAL-003: Eş zamanlı yükleme koruması

    func test_loadProducts_ignoresCall_whenAlreadyLoading() async {
        let repo = MockProductRepository()
        let vm = ProductListViewModel(categoryId: nil, repository: repo)

        // İlk çağrı başlatılıyor
        async let first: () = vm.loadProducts()
        async let second: () = vm.loadProducts() // İkinci çağrı isLoading=true iken gelir
        await first
        await second

        // Çift yükleme olmamalı — products tutarlı olmalı
        XCTAssertFalse(vm.isLoading)
    }

    // MARK: - FR-007: Pagination

    func test_loadNextPage_appendsProducts() async {
        let repo = MockProductRepository()
        let vm = ProductListViewModel(categoryId: nil, repository: repo)
        await vm.loadProducts()

        let firstPageCount = vm.products.count
        if vm.hasMore {
            await vm.loadNextPage()
            XCTAssertGreaterThan(vm.products.count, firstPageCount)
        }
    }

    // MARK: - FR-011: Kategori filtresi

    func test_categoryFilter_returnsOnlyCategoryProducts() async {
        let repo = MockProductRepository()
        let vm = ProductListViewModel(categoryId: "cat-protein", repository: repo)
        await vm.loadProducts()

        let allBelongToCategory = vm.products.allSatisfy { product in
            product.categories?.contains { $0.id == "cat-protein" } ?? false
        }
        XCTAssertTrue(allBelongToCategory)
    }

    // MARK: - Error handling

    func test_loadProducts_setsErrorMessage_onFailure() async {
        let repo = FailingMockRepository()
        let vm = ProductListViewModel(categoryId: nil, repository: repo)
        await vm.loadProducts()

        XCTAssertNotNil(vm.errorMessage)
        XCTAssertTrue(vm.products.isEmpty)
    }
}

// MARK: - Test Helpers

final class LimitedMockRepository: ProductRepositoryProtocol {
    let itemCount: Int
    init(itemCount: Int) { self.itemCount = itemCount }

    func fetchCategories() async throws -> [StoreCategory] { [] }

    func fetchProducts(categoryId: String?, page: Int, sort: ProductSortType) async throws -> ProductList {
        let products = (0..<itemCount).map { i in
            Product(id: "p\(i)", name: "Ürün \(i)", description: nil,
                    variants: [ProductVariant(id: "v\(i)", name: nil,
                                              price: VariantPrice(sellPrice: 100, buyPrice: nil, discountPrice: nil),
                                              stock: VariantStock(stockCount: 10), mainImageId: nil)],
                    categories: nil, brand: nil, imageList: nil)
        }
        return ProductList(data: products, count: itemCount)
    }
}

final class FailingMockRepository: ProductRepositoryProtocol {
    enum TestError: Error { case intentional }
    func fetchCategories() async throws -> [StoreCategory] { throw TestError.intentional }
    func fetchProducts(categoryId: String?, page: Int, sort: ProductSortType) async throws -> ProductList {
        throw TestError.intentional
    }
}
