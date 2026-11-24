import Foundation

/// Deterministic Tool: Checks syllabus coverage readiness against the 80% benchmark (Unit 3-4)
public struct ExamReadinessTool: Sendable {
    public static let benchmarkThreshold: Double = 80.0

    public struct Result: Sendable, Equatable {
        public let percentage: Double
        public let isReady: Bool
        public let remainingTopics: Int
        public let message: String
    }

    public enum ToolError: Error, LocalizedError, Sendable {
        case negativeTopicsCovered
        case nonPositiveTotalTopics
        case coveredExceedsTotal

        public var errorDescription: String? {
            switch self {
            case .negativeTopicsCovered:
                return "Topics covered cannot be negative."
            case .nonPositiveTotalTopics:
                return "Total topics must be greater than zero."
            case .coveredExceedsTotal:
                return "Topics covered cannot exceed total topics."
            }
        }
    }

    public static func evaluate(topicsCovered: Int, totalTopics: Int) -> Swift.Result<Result, ToolError> {
        guard topicsCovered >= 0 else {
            return .failure(.negativeTopicsCovered)
        }
        guard totalTopics > 0 else {
            return .failure(.nonPositiveTotalTopics)
        }
        guard topicsCovered <= totalTopics else {
            return .failure(.coveredExceedsTotal)
        }

        let percentage = (Double(topicsCovered) / Double(totalTopics)) * 100.0
        let isReady = percentage >= benchmarkThreshold
        let remaining = totalTopics - topicsCovered

        let statusText = isReady ? "Ready (Threshold met >= 80%)" : "Not ready yet (Below 80% benchmark)"
        let message = "\(statusText): \(topicsCovered)/\(totalTopics) topics completed (\(String(format: "%.1f", percentage))%). Remaining topics: \(remaining)."

        return .success(Result(
            percentage: percentage,
            isReady: isReady,
            remainingTopics: remaining,
            message: message
        ))
    }
}
