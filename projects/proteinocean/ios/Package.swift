// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ProteinOcean",
    platforms: [
        .iOS(.v17)
    ],
    targets: [
        .executableTarget(
            name: "ProteinOcean",
            path: "ProteinOcean",
            sources: [
                "App",
                "Core/Network",
                "Core/Models",
                "Core/Extensions",
                "Features/Categories/Views",
                "Features/Categories/ViewModels",
                "Features/Products/Views",
                "Features/Products/ViewModels",
                "Resources"
            ]
        )
    ]
)
