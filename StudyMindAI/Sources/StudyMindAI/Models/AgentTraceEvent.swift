import Foundation

/// Represents a single reasoning or execution step in the ReAct / Multi-Agent trace (Unit 1 & Unit 4)
public struct AgentTraceEvent: Codable, Identifiable, Sendable, Equatable {
    public enum StepType: String, Codable, Sendable {
        case thought = "THOUGHT"
        case action = "ACTION"
        case observation = "OBSERVATION"
        case guardrailBlock = "GUARDRAIL_BLOCK"
        case hitlPrompt = "HITL_PROMPT"
        case hitlDecision = "HITL_DECISION"
        case synthesis = "SYNTHESIS"
    }

    public var id: UUID
    public var timestamp: Date
    public var hopIndex: Int
    public var agentName: String
    public var stepType: StepType
    public var title: String
    public var detail: String
    public var isWarningOrError: Bool

    public init(
        id: UUID = UUID(),
        timestamp: Date = Date(),
        hopIndex: Int = 0,
        agentName: String,
        stepType: StepType,
        title: String,
        detail: String,
        isWarningOrError: Bool = false
    ) {
        self.id = id
        self.timestamp = timestamp
        self.hopIndex = hopIndex
        self.agentName = agentName
        self.stepType = stepType
        self.title = title
        self.detail = detail
        self.isWarningOrError = isWarningOrError
    }
}
