import Foundation

struct GraphQLRequest: Encodable {
    let query: String
    let variables: [String: AnyEncodable]?

    init(query: String, variables: [String: AnyEncodable]? = nil) {
        self.query = query
        self.variables = variables
    }
}

struct GraphQLResponse<T: Decodable>: Decodable {
    let data: T?
    let errors: [GraphQLError]?
}

struct GraphQLError: Decodable {
    let message: String
}

enum NetworkError: LocalizedError {
    case invalidURL
    case noData
    case decodingFailed(Error)
    case apiError(String)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Geçersiz URL"
        case .noData: return "Veri alınamadı"
        case .decodingFailed(let e): return "Veri işleme hatası: \(e.localizedDescription)"
        case .apiError(let msg): return msg
        case .unauthorized: return "API token geçersiz. ikas admin panelinden token oluşturun."
        }
    }
}

actor GraphQLClient {
    static let shared = GraphQLClient()

    private let session: URLSession

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.requestCachePolicy = .returnCacheDataElseLoad
        session = URLSession(configuration: config)
    }

    func execute<T: Decodable>(_ request: GraphQLRequest, as type: T.Type) async throws -> T {
        guard let url = URL(string: IkasAPIConfig.graphQLEndpoint) else {
            throw NetworkError.invalidURL
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(IkasAPIConfig.bearerToken)", forHTTPHeaderField: "Authorization")

        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await session.data(for: urlRequest)

        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }

        let graphQLResponse = try JSONDecoder().decode(GraphQLResponse<T>.self, from: data)

        if let errors = graphQLResponse.errors, !errors.isEmpty {
            throw NetworkError.apiError(errors.map(\.message).joined(separator: ", "))
        }

        guard let result = graphQLResponse.data else {
            throw NetworkError.noData
        }

        return result
    }
}

// AnyEncodable helper
struct AnyEncodable: Encodable {
    private let _encode: (Encoder) throws -> Void

    init<T: Encodable>(_ value: T) {
        _encode = value.encode
    }

    func encode(to encoder: Encoder) throws {
        try _encode(encoder)
    }
}
