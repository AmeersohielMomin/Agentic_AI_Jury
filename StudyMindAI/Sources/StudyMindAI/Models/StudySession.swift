import Foundation

/// Represents a scheduled study task or session in the plan (Unit 2 & 4)
public struct StudySession: Codable, Identifiable, Sendable, Equatable {
    public var id: UUID
    public var dayIndex: Int
    public var topicName: String
    public var allocatedHours: Double
    public var isCompleted: Bool
    public var difficultyTag: String

    public init(
        id: UUID = UUID(),
        dayIndex: Int,
        topicName: String,
        allocatedHours: Double,
        isCompleted: Bool = false,
        difficultyTag: String = "Normal"
    ) {
        self.id = id
        self.dayIndex = dayIndex
        self.topicName = topicName
        self.allocatedHours = allocatedHours
        self.isCompleted = isCompleted
        self.difficultyTag = difficultyTag
    }
}
