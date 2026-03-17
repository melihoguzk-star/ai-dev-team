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
            path: "ProteinOcean"
        )
    ]
)
