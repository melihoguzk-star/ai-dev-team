# SwiftUI Liste Ekranı — Item Yönetimi

> **Hedef:** iOS 17+ | Swift 5.9+ | `@Observable` macro | SwiftUI

---

## 1. Veri Modeli — `Item`

`Identifiable` protokolüne uygun, basit bir değer tipi. `Hashable` uyumu sayesinde `List` ve `ForEach` ile doğrudan kullanılabilir.

```swift
import Foundation

struct Item: Identifiable, Hashable {
    let id: UUID
    var title: String
    var description: String
    var isCompleted: Bool

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        isCompleted: Bool = false
    ) {
        self.id = id
        self.title = title
        self.description = description
    }
}
```

---

## 2. ViewModel — `ItemListViewModel`

iOS 17 ile gelen `@Observable` macro'su kullanılıyor. Eski `ObservableObject` / `@Published` kalıbına gerek yok; SwiftUI değişiklikleri otomatik olarak izler.

```swift
import Foundation
import Observation

@Observable
final class ItemListViewModel {

    // MARK: - State

    /// Görüntülenen öğe listesi
    var items: [Item] = []

    /// Yeni öğe ekleme sheet'i için kontrol değişkeni
    var isAddSheetPresented: Bool = false

    // MARK: - Actions

    /// Listeye yeni bir öğe ekler.
    /// - Parameters:
    ///   - title: Öğe başlığı
    ///   - description: Öğe açıklaması
    func addItem(title: String, description: String) async {
        // Gerçek bir projede burada ağ isteği veya veritabanı yazımı olabilir.
        let newItem = Item(title: title, description: description)
        items.append(newItem)
    }

    /// Belirtilen öğenin tamamlanma durumunu tersine çevirir.
    /// - Parameter id: Hedef öğenin UUID'si
    func toggleComplete(for id: UUID) {
        guard let index = items.firstIndex(where: { $0.id == id }) else { return }
        items[index].isCompleted.toggle()
    }

    /// Verilen index set'teki öğeleri listeden siler (swipe-to-delete desteği).
    /// - Parameter offsets: Silinecek indeksler
    func deleteItems(at offsets: IndexSet) {
        items.remove(atOffsets: offsets)
    }

    /// Tek bir öğeyi id üzerinden siler.
    /// - Parameter id: Silinecek öğenin UUID'si
    func deleteItem(by id: UUID) {
        items.removeAll { $0.id == id }
    }
}
```

### Neden `@Observable`?

| Özellik | `ObservableObject` (eski) | `@Observable` (iOS 17+) |
|---|---|---|
| Property wrapper | `@Published` gerekir | Gerek yok — otomatik izleme |
| View tarafı | `@ObservedObject` / `@StateObject` | `@State` veya doğrudan referans |
| Performans | Her `@Published` değişikliğinde tüm body yeniden hesaplanır | Yalnızca okunan property değiştiğinde yeniden hesaplama |

---

## 3. View Katmanı

### 3.1 `ItemListView` — Ana Liste Ekranı

```swift
import SwiftUI

struct ItemListView: View {

    @State private var viewModel = ItemListViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.items.isEmpty {
                    emptyStateView
                } else {
                    itemList
                }
            }
            .navigationTitle("Öğelerim")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        viewModel.isAddSheetPresented = true
                    } label: {
                        Image(systemName: "plus")
                    }
                    .accessibilityLabel("Yeni öğe ekle")
                }
            }
            .sheet(isPresented: $viewModel.isAddSheetPresented) {
                AddItemView(viewModel: viewModel)
            }
        }
    }

    // MARK: - Alt Bileşenler

    /// Liste boşken gösterilen bilgilendirme ekranı.
    private var emptyStateView: some View {
        ContentUnavailableView(
            "Henüz öğe yok",
            systemImage: "tray",
            description: Text("Sağ üstteki + butonuna tıklayarak yeni bir öğe ekleyebilirsiniz.")
        )
    }

    /// Öğelerin listelendiği ana görünüm.
    private var itemList: some View {
        List {
            ForEach(viewModel.items) { item in
                ItemRowView(item: item) {
                    viewModel.toggleComplete(for: item.id)
                }
            }
            .onDelete { offsets in
                viewModel.deleteItems(at: offsets)
            }
        }
        .listStyle(.insetGrouped)
        .animation(.default, value: viewModel.items)
    }
}
```

> **Not:** `ContentUnavailableView` iOS 17 ile gelen yerleşik bir empty-state bileşenidir. Önceki sürümlerde bu bileşeni manuel olarak oluşturmak gerekirdi.

---

### 3.2 `ItemRowView` — Satır Bileşeni

Her bir öğeyi gösteren, tamamlanma durumunu toggle edebilen satır.

```swift
import SwiftUI

struct ItemRowView: View {

    let item: Item
    let onToggle: () -> Void

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Button {
                onToggle()
            } label: {
                Image(systemName: item.isCompleted ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(item.isCompleted ? .green : .secondary)
                    .imageScale(.large)
                    .contentTransition(.symbolEffect(.replace))
            }
            .buttonStyle(.plain)
            .accessibilityLabel(item.isCompleted ? "Tamamlandı" : "Tamamlanmadı")

            VStack(alignment: .leading, spacing: 4) {
                Text(item.title)
                    .font(.headline)
                    .strikethrough(item.isCompleted, color: .secondary)
                    .foregroundStyle(item.isCompleted ? .secondary : .primary)

                if !item.description.isEmpty {
                    Text(item.description)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
            }
        }
        .padding(.vertical, 4)
    }
}
```

> **Not:** `.contentTransition(.symbolEffect(.replace))` iOS 17'de eklenen SF Symbol animasyonlarını kullanır. Checkbox geçişi akıcı bir animasyonla gerçekleşir.

---

### 3.3 `AddItemView` — Yeni Öğe Ekleme Sheet'i

```swift
import SwiftUI

struct AddItemView: View {

    let viewModel: ItemListViewModel

    @Environment(\.dismiss) private var dismiss

    @State private var title: String = ""
    @State private var description: String = ""

    /// Form geçerli mi kontrolü
    private var isFormValid: Bool {
        !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Detaylar") {
                    TextField("Başlık", text: $title)
                        .textInputAutocapitalization(.sentences)

                    TextField("Açıklama (isteğe bağlı)", text: $description, axis: .vertical)
                        .lineLimit(3...6)
                }
            }
            .navigationTitle("Yeni Öğe")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        Task {
                            await viewModel.addItem(
                                title: title.trimmingCharacters(in: .whitespacesAndNewlines),
                                description: description.trimmingCharacters(in: .whitespacesAndNewlines)
                            )
                            dismiss()
                        }
                    }
                    .disabled(!isFormValid)
                }
            }
        }
        .presentationDetents([.medium])
        .presentationDragIndicator(.visible)
    }
}
```

---

### 3.4 `#Preview` Makroları

iOS 17 ile gelen `#Preview` makrosu, eski `PreviewProvider` protokolünü değiştirir.

```swift
// MARK: - Previews

#Preview("Liste — Dolu") {
    let vm = ItemListViewModel()
    vm.items = [
        Item(title: "Market alışverişi", description: "Süt, ekmek, yumurta"),
        Item(title: "Spor", description: "18:00 — Kardiyo + ağırlık", isCompleted: true),
        Item(title: "Kitap oku", description: "Clean Architecture — 3. bölüm"),
    ]
    return ItemListView()
}

#Preview("Liste — Boş") {
    ItemListView()
}
```

---

## 4. Uygulama Giriş Noktası

```swift
import SwiftUI

@main
struct ItemTrackerApp: App {
    var body: some Scene {
        WindowGroup {
            ItemListView()
        }
    }
}
```

---

## 5. Mimari Özet

```
┌─────────────────────────────────────────────┐
│                   App                        │
│  ┌───────────────────────────────────────┐   │
│  │          ItemListView                 │   │
│  │  @State var viewModel                 │   │
│  │  ┌─────────────┐  ┌───────────────┐   │   │
│  │  │ ItemRowView  │  │ AddItemView   │   │   │
│  │  │ (per item)   │  │ (sheet)       │   │   │
│  │  └──────┬───────┘  └───────┬───────┘   │   │
│  └─────────┼──────────────────┼───────────┘   │
│            │                  │               │
│  ┌─────────▼──────────────────▼───────────┐   │
│  │       ItemListViewModel (@Observable)  │   │
│  │  items: [Item]                         │   │
│  │  addItem / toggleComplete / delete     │   │
│  └────────────────────────────────────────┘   │
│                                               │
│  ┌────────────────────────────────────────┐   │
│  │       Item (struct, Identifiable)      │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 6. Kullanılan iOS 17+ API'leri

| API | Kullanım Yeri | Açıklama |
|---|---|---|
| `@Observable` macro | `ItemListViewModel` | `ObservableObject` yerine modern izleme mekanizması |
| `ContentUnavailableView` | `ItemListView` | Yerleşik empty-state bileşeni |
| `.contentTransition(.symbolEffect(.replace))` | `ItemRowView` | SF Symbol animasyon geçişi |
| `#Preview` macro | Previews | Eski `PreviewProvider` yerine kısa syntax |
| `.presentationDetents([.medium])` | `AddItemView` | Sheet yükseklik kontrolü |
| `TextField(axis: .vertical)` | `AddItemView` | Çok satırlı metin alanı |
