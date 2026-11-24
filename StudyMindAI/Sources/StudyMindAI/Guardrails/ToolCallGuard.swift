import Foundation

/// Layer 2 Safety Guardrail: Verifies deterministic invariants and operational bounds for tool calls (Unit 5)
public struct ToolCallGuard: Sendable {
    public struct GuardCheck: Sendable, Equatable {
        public let allowed: Bool
        public let reason: String?
    }

    public static func validateReadinessParameters(topicsCovered: Int, totalTopics: Int) -> GuardCheck {
        if topicsCovered < 0 {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: topicsCovered (\(topicsCovered)) cannot be negative.")
        }
        if totalTopics <= 0 {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: totalTopics (\(totalTopics)) must be greater than zero.")
        }
        if topicsCovered > totalTopics {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: topicsCovered (\(topicsCovered)) exceeds totalTopics (\(totalTopics)).")
        }
        return GuardCheck(allowed: true, reason: nil)
    }

    public static func validateHoursParameters(
        topicsCovered: Int,
        totalTopics: Int,
        daysLeft: Int,
        hoursPerTopic: Double
    ) -> GuardCheck {
        if daysLeft < 0 {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: daysLeft (\(daysLeft)) cannot be negative.")
        }
        if hoursPerTopic < 0 {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: hoursPerTopic (\(hoursPerTopic)) cannot be negative.")
        }
        if topicsCovered > totalTopics {
            return GuardCheck(allowed: false, reason: "Tool parameter violation: topicsCovered exceeds totalTopics.")
        }
        return GuardCheck(allowed: true, reason: nil)
    }

    public static func validateProposedWorkload(hoursPerDay: Double) -> GuardCheck {
        if hoursPerDay > 16.0 {
            return GuardCheck(
                allowed: false,
                reason: "Tool output rejected: Proposed workload of \(String(format: "%.1f", hoursPerDay))h/day exceeds absolute human physiological safety limit (16h). Schedule rejected as dangerous."
            )
        }
        return GuardCheck(allowed: true, reason: nil)
    }
}
