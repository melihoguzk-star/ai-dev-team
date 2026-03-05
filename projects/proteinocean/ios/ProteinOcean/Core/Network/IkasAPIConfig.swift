import Foundation

enum IkasAPIConfig {
    // Mock modu: true → MockProductRepository, false → gerçek ikas API
    // Token alındığında false yapıp IKAS_API_TOKEN env variable ekle
    static let useMockData = true

    static let graphQLEndpoint = "https://api.myikas.com/api/v1/admin/graphql"

    static var bearerToken: String {
        ProcessInfo.processInfo.environment["IKAS_API_TOKEN"] ?? ""
    }

    static func makeRepository() -> ProductRepositoryProtocol {
        useMockData ? MockProductRepository() : ProductRepository()
    }
}
