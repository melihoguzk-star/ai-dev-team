import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            CategoriesView()
                .tabItem {
                    Label("Kategoriler", systemImage: "square.grid.2x2")
                }

            ProductListView(title: "Tüm Ürünler", categoryId: nil)
                .tabItem {
                    Label("Ürünler", systemImage: "bag")
                }
        }
        .tint(Color.brandPrimary)
        .toolbarBackground(.visible, for: .tabBar)
        .toolbarBackground(Color.brandBackground, for: .tabBar)
    }
}
