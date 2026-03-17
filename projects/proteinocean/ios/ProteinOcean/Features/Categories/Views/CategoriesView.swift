import SwiftUI

struct CategoriesView: View {
    @State private var viewModel = CategoriesViewModel()
    @State private var selectedStoreCategory: StoreCategory?

    private let columns = [
        GridItem(.flexible()),
        GridItem(.flexible())
    ]

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        Task { await viewModel.loadCategories() }
                    }
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: BrandStyle.Spacing.section) {
                            ForEach(viewModel.rootCategories) { category in
                                NavigationLink(value: category) {
                                    StoreCategoryCard(category: category)
                                }
                            }
                        }
                        .padding(BrandStyle.Spacing.page)
                    }
                }
            }
            .background(Color.brandBackground)
            .clipShape(UnevenRoundedRectangle(
                topLeadingRadius: BrandStyle.Radius.page,
                bottomLeadingRadius: 0,
                bottomTrailingRadius: 0,
                topTrailingRadius: BrandStyle.Radius.page
            ))
            .background(Color.brandPrimary)
            .navigationTitle("Kategoriler")
            .navigationBarTitleDisplayMode(.inline)
            .navigationDestination(for: StoreCategory.self) { category in
                ProductListView(
                    title: category.name,
                    categoryId: category.id
                )
            }
            .task {
                await viewModel.loadCategories()
            }
            .toolbarBackground(Color.brandPrimary, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbarColorScheme(.dark, for: .navigationBar)
        }
    }
}

struct StoreCategoryCard: View {
    let category: StoreCategory

    var body: some View {
        VStack(spacing: 0) {
            AsyncImage(url: category.imageUrl.flatMap(URL.init)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                StoreCategoryPlaceholderImage(name: category.name)
            }
            .frame(height: 120)
            .clipped()

            VStack(alignment: .leading, spacing: 4) {
                Text(category.name)
                    .font(.brandSectionHead)
                    .foregroundStyle(.primary)
                    .lineLimit(2)

                if let count = category.productCount {
                    Text("\(count) ürün")
                        .font(.brandCaption)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(12)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(Color.brandBackground)
        .clipShape(RoundedRectangle(cornerRadius: BrandStyle.Radius.card))
        .shadow(color: .black.opacity(0.08), radius: 6, x: 0, y: 2)
    }
}

struct StoreCategoryPlaceholderImage: View {
    let name: String

    private var emoji: String {
        let map: [String: String] = [
            "protein": "💪",
            "vitamin": "💊",
            "gida": "🥗",
            "aksesuar": "🎽",
            "paket": "📦",
            "promosyon": "🏷️",
            "saglik": "❤️"
        ]
        let key = name.lowercased()
        return map.first(where: { key.contains($0.key) })?.value ?? "🛒"
    }

    var body: some View {
        Rectangle()
            .fill(Color.brandPrimary.opacity(0.08))
            .overlay {
                Text(emoji)
                    .font(.system(size: 44))
            }
    }
}

struct ErrorView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 44))
                .foregroundStyle(Color.brandWarning)

            Text(message)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)

            Button("Tekrar Dene", action: retry)
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview("Kategoriler") {
    CategoriesView()
}
