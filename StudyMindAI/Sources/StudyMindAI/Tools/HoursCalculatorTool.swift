import Foundation

/// Deterministic Tool: Computes daily required study hours with defensive boundary handling (Unit 3-4)
public struct HoursCalculatorTool: Sendable {
    public static let biologicalLimitHoursPerDay: Double = 12.0

    public struct Result: Sendable, Equatable {
        public let hoursPerDay: Double
        public let remainingTopics: Int
        public let totalRequiredHours: Double
        public let isOverBiologicalLimit: Bool
        public let explanation: String
    }

    public enum ToolError: Error, LocalizedError, Sendable {
        case zeroDaysLeft
        case negativeDaysLeft
        case negativeHoursPerTopic
        case negativeRemainingTopics

        public var errorDescription: String? {
            switch self {
            case .zeroDaysLeft:
                return "days_left must be greater than zero. Cannot divide remaining study hours across 0 days."
            case .negativeDaysLeft:
                return "days_left cannot be negative."
            case .negativeHoursPerTopic:
                return "hours_per_topic cannot be negative."
            case .negativeRemainingTopics:
                return "remaining topics cannot be negative."
            }
        }
    }

    public static func calculate(
        topicsCovered: Int,
        totalTopics: Int,
        daysLeft: Int,
        hoursPerTopic: Double
    ) -> Swift.Result<Result, ToolError> {
        guard daysLeft > 0 else {
            if daysLeft == 0 {
                return .failure(.zeroDaysLeft)
            } else {
                return .failure(.negativeDaysLeft)
            }
        }
        guard hoursPerTopic >= 0 else {
            return .failure(.negativeHoursPerTopic)
        }
        guard totalTopics >= topicsCovered else {
            return .failure(.negativeRemainingTopics)
        }

        let remaining = totalTopics - topicsCovered
        let totalHours = Double(remaining) * hoursPerTopic
        let hoursPerDay = totalHours / Double(daysLeft)
        let isOverLimit = hoursPerDay > biologicalLimitHoursPerDay

        var explanation = "Requires \(String(format: "%.2f", hoursPerDay)) study hours/day (\(remaining) remaining topics × \(hoursPerTopic)h ÷ \(daysLeft) days)."
        if isOverLimit {
            explanation += " WARNING: Exceeds realistic biological ceiling of \(biologicalLimitHoursPerDay)h/day! High burnout risk."
        }

        return .success(Result(
            hoursPerDay: hoursPerDay,
            remainingTopics: remaining,
            totalRequiredHours: totalHours,
            isOverBiologicalLimit: isOverLimit,
            explanation: explanation
        ))
    }
}
