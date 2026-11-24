import Foundation

/// Represents a persistent student profile used by Long-Term Memory (Unit 3-2)
public struct StudentProfile: Codable, Identifiable, Sendable, Equatable {
    public var id: UUID
    public var studentId: String
    public var name: String
    public var targetSubject: String
    public var staminaHoursPerDay: Double
    public var historicalScores: [Double]
    public var notes: String
    public var createdAt: Date
    public var updatedAt: Date

    public init(
        id: UUID = UUID(),
        studentId: String,
        name: String,
        targetSubject: String,
        staminaHoursPerDay: Double = 4.0,
        historicalScores: [Double] = [],
        notes: String = "",
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.studentId = studentId
        self.name = name
        self.targetSubject = targetSubject
        self.staminaHoursPerDay = staminaHoursPerDay
        self.historicalScores = historicalScores
        self.notes = notes
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}
