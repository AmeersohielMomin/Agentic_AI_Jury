import Foundation

/// Represents an on-device knowledge chunk for syllabus guidelines retrieval (Unit 3-3)
public struct SyllabusChunk: Codable, Identifiable, Sendable, Equatable {
    public var id: String
    public var subject: String
    public var topic: String
    public var section: String
    public var content: String
    public var recommendedHours: Double
    public var keywords: [String]

    public init(
        id: String,
        subject: String,
        topic: String,
        section: String,
        content: String,
        recommendedHours: Double,
        keywords: [String] = []
    ) {
        self.id = id
        self.subject = subject
        self.topic = topic
        self.section = section
        self.content = content
        self.recommendedHours = recommendedHours
        self.keywords = keywords
    }
}
