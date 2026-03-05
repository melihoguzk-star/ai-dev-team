import SwiftUI

struct ProductListView: View {
    let title: String
    let categoryId: String?

    @State private var viewModel: ProductListViewModel
    @State private var showSortSheet = false
    @State private var isGridLayout = true

    init(title: String, categoryId: String? = nil) {
        self.title = title
        self.categoryId = categoryId
        _viewModel = State(initialValue: ProductListViewModel(categoryId: categoryId))
    }

    private let gridColumns = [
        GridItem(.flexible(), spacing: 12),
        GridItem(.flexible(), spacing: 12)
    ]

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar: Sort + Layout toggle
            HStack {
                Button {
                    showSortSheet = true
                } label: {
                    Label(viewModel.currentSort.displayName, systemImage: "arrow.up.arrow.down")
                        .font(.subheadline)
                }

                Spacer()

                Button {
                    withAnimation { isGridLayout.toggle() }
                } label: {
                    Image(systemName: isGridLayout ? "list.bullet" : "square.grid.2x2")
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 10)
            .background(Color(.systemGroupedBackground))

            Divider()

            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                ErrorView(message: error) {
                    Task { await viewModel.loadProducts() }
                }
            } else {
                ScrollView {
                    if isGridLayout {
                        LazyVGrid(columns: gridColumns, spacing: 12) {
                            ForEach(viewModel.products) { product in
                                ProductCard(product: product, isGrid: true)
                                    .onAppear {
                                        if product.id == viewModel.products.last?.id {
                                            Task { await viewModel.loadNextPage() }
                                        }
                                    }
                            }
                        }
                        .padding()
                    } else {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.products) { product in
                                ProductCard(product: product, isGrid: false)
                                    .onAppear {
                                        if product.id == viewModel.products.last?.id {
                                            Task { await viewModel.loadNextPage() }
                                        }
                                    }
                            }
                        }
                        .padding()
                    }

                    if viewModel.isLoadingMore {
                        ProgressView()
                            .padding()
                    }
                }
            }
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await viewModel.loadProducts()
        }
        .confirmationDialog("Siralama", isPresented: $showSortSheet) {
            ForEach(ProductSortType.allCases, id: \.rawValue) { sort in
                Button(sort.displayName) {
                    viewModel.setSort(sort)
                }
            }
        }
    }
}

struct ProductCard: View {
    let product: Product
    let isGrid: Bool

    var body: some View {
        if isGrid {
            gridCard
        } else {
            listCard
        }
    }

    private var gridCard: some View {
        VStack(alignment: .leading, spacing: 0) {
            productImage
                .frame(height: 160)
                .clipped()

            VStack(alignment: .leading, spacing: 6) {
                Text(product.name)
                    .font(.subheadline)
                    .lineLimit(2)
                    .foregroundStyle(.primary)

                priceView
            }
            .padding(10)
        }
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.07), radius: 5, x: 0, y: 2)
        .overlay(alignment: .topTrailing) {
            discountBadge
        }
    }

    private var listCard: some View {
        HStack(spacing: 12) {
            productImage
                .frame(width: 90, height: 90)
                .clipShape(RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading, spacing: 6) {
                Text(product.name)
                    .font(.subheadline)
                    .lineLimit(3)

                if let brand = product.brand {
                    Text(brand.name)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                priceView

                stockBadge
            }

            Spacer()
        }
        .padding(12)
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.07), radius: 5, x: 0, y: 2)
    }

    private var productImage: some View {
        Group {
            if let imageUrl = product.mainImage?.cdnUrl, let url = URL(string: imageUrl) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image.resizable().aspectRatio(contentMode: .fill)
                    case .failure:
                        placeholderImage
                    default:
                        ProgressView()
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(Color(.systemGray6))
                    }
                }
            } else {
                placeholderImage
            }
        }
    }

    private var placeholderImage: some View {
        Rectangle()
            .fill(Color(.systemGray5))
            .overlay {
                Image(systemName: "photo")
                    .foregroundStyle(.secondary)
            }
    }

    private var priceView: some View {
        VStack(alignment: .leading, spacing: 2) {
            if let sellPrice = product.minPrice {
                Text(sellPrice.formatted(.currency(code: "TRY")))
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundStyle(.blue)
            }

            if let originalPrice = product.originalPrice,
               let sellPrice = product.minPrice,
               originalPrice > sellPrice {
                Text(originalPrice.formatted(.currency(code: "TRY")))
                    .font(.caption)
                    .strikethrough()
                    .foregroundStyle(.secondary)
            }
        }
    }

    @ViewBuilder
    private var discountBadge: some View {
        if let discount = product.discountPercent {
            Text("%-\(discount)")
                .font(.caption2)
                .fontWeight(.bold)
                .foregroundStyle(.white)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(.red)
                .clipShape(RoundedRectangle(cornerRadius: 6))
                .padding(8)
        }
    }

    @ViewBuilder
    private var stockBadge: some View {
        if !product.isInStock {
            Text("Stokta Yok")
                .font(.caption2)
                .foregroundStyle(.orange)
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(Color.orange.opacity(0.12))
                .clipShape(Capsule())
        }
    }
}

#Preview("Tüm Ürünler") {
    ProductListView(title: "Tüm Ürünler")
}

#Preview("Protein Kategorisi") {
    NavigationStack {
        ProductListView(title: "Protein", categoryId: "cat-protein")
    }
}

#Preview("Ürün Kartı - Grid") {
    ProductCard(product: MockData.products[0], isGrid: true)
        .frame(width: 180)
        .padding()
}

#Preview("Ürün Kartı - Liste") {
    ProductCard(product: MockData.products[2], isGrid: false)
        .padding()
}
