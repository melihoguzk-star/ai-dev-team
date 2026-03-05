import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            CategoriesView()
                .tabItem {
                    Label("Kategoriler", systemImage: "square.grid.2x2")
                }

            ProductListView(title: "Tum Urunler", categoryId: nil)
                .tabItem {
                    Label("Urunler", systemImage: "bag")
                }
        }
        .tint(.blue)
    }
}
