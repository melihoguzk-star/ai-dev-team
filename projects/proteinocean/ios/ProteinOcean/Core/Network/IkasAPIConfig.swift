import Foundation

enum IkasAPIConfig {
    // ikas Admin API endpoint
    // Token: ikas Admin Panel → Ayarlar → Geliştirici → Private App oluştur
    static let graphQLEndpoint = "https://api.myikas.com/api/v1/admin/graphql"

    // TODO: Buraya ikas Private App token'ınızı ekleyin
    static var bearerToken: String {
        // Gerçek kullanım: Bundle/Keychain'den oku
        ProcessInfo.processInfo.environment["IKAS_API_TOKEN"] ?? ""
    }
}
