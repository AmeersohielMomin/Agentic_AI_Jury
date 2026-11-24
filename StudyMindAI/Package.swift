// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "StudyMindAI",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .executable(
            name: "StudyMindAI",
            targets: ["StudyMindAI"]
        )
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "StudyMindAI",
            dependencies: [],
            path: "Sources/StudyMindAI"
        ),
        .testTarget(
            name: "StudyMindAITests",
            dependencies: ["StudyMindAI"],
            path: "Tests/StudyMindAITests"
        )
    ]
)
