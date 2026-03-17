import SwiftUI

@main
struct ProteinOceanApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

// MARK: - Brand Colors
extension Color {
    /// Hex string'den Color oluşturur. "#2126AB" veya "2126AB" formatını kabul eder.
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r, g, b, a: UInt64
        switch hex.count {
        case 6:  (r, g, b, a) = (int >> 16, int >> 8 & 0xFF, int & 0xFF, 255)
        case 8:  (r, g, b, a) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default: (r, g, b, a) = (0, 0, 0, 255)
        }
        self.init(.sRGB,
                  red: Double(r) / 255,
                  green: Double(g) / 255,
                  blue: Double(b) / 255,
                  opacity: Double(a) / 255)
    }

    static let brandPrimary             = Color(hex: "#2126AB")  // Navigasyon, tint
    static let brandSecondary           = Color(hex: "#232DA8")  // Fiyat rengi
    static let brandAccent              = Color(hex: "#1900FF")  // CTA border
    static let brandError               = Color(hex: "#DB2626")  // İndirim badge, hata durumu
    static let brandWarning             = Color(hex: "#FF6600")  // Lansman badge, stok uyarısı
    static let brandBorder              = Color(hex: "#E5E5E5")  // Kart border, divider
    // Background — brand-tokens.json: background
    static let brandBackground          = Color(hex: "#FFFFFF")  // Kart, sayfa arka planı
    static let brandBackgroundSecondary = Color(hex: "#F8F8F8")  // Toolbar, grouped bg (Figma --background/100)
    // Text — brand-tokens.json: text
    static let brandTextPrimary         = Color(hex: "#070707")  // Başlıklar, ana metin
    static let brandTextSecondary       = Color(hex: "#464646")  // İkincil metin (Figma --neutral/gray-800)
}

// MARK: - Brand Typography
extension Font {
    // Figma: Montserrat — Xcode projesine Montserrat-{SemiBold,Medium,Light,Bold}.ttf ekle
    static let brandNavTitle    = Font.custom("Montserrat-SemiBold", size: 18)  // Nav bar başlık
    static let brandSectionHead = Font.custom("Montserrat-SemiBold", size: 16)  // Kart başlığı
    static let brandBody        = Font.custom("Montserrat-Light",    size: 14)  // Açıklama metni
    static let brandCaption     = Font.custom("Montserrat-Medium",   size: 12)  // Badge, etiket
    static let brandPrice       = Font.custom("Montserrat-Bold",     size: 16)  // Fiyat
}

// MARK: - Brand Layout
enum BrandStyle {
    enum Spacing {
        static let page: CGFloat    = 20  // Figma: yatay sayfa padding
        static let grid: CGFloat    = 12  // Figma: ürün grid boşluğu
        static let section: CGFloat = 16  // Bölüm arası boşluk
        static let card: CGFloat    = 12  // Kart içi padding
    }
    enum Radius {
        static let page: CGFloat   = 20  // Figma: sayfa üst köşe
        static let card: CGFloat   = 12  // Ürün kartı, kategori kartı
        static let button: CGFloat =  8  // Primary / secondary buton
        static let input: CGFloat  =  8  // Input, arama kutusu
        static let badge: CGFloat  =  6  // İndirim badge
    }
    enum Size {
        static let buttonHeight: CGFloat       = 56   // Figma: primary/secondary
        static let inputHeight: CGFloat        = 50   // Figma: input/search
        static let productCardWidth: CGFloat   = 172  // Figma: 2-kolon grid
        static let productImageHeight: CGFloat = 160  // Figma: kart görseli
    }
}
