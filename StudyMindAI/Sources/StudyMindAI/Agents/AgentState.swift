import Foundation

/// Represents the shared state container flowing through the multi-agent graph (Unit 4-2)
public struct AgentState: Sendable {
    public var query: String
    public var studentId: String
    public var subject: String
    public var topicsCovered: Int
    public var totalTopics: Int
    public var daysLeft: Int
    public var hoursPerTopic: Double
    public var staminaHoursPerDay: Double

    // Diagnostician Outputs
    public var readinessScore: Double?
    public var isReady: Bool?
    public var readinessAssessment: String?
    public var ragSnippets: [String]

    // Workload Planner Outputs
    public var calculatedHoursPerDay: Double?
    public var negotiatedHoursPerDay: Double?
    public var isOverStamina: Bool
    public var planProposal: String?

    // Multi-Agent & Orchestration Control
    public var hopCount: Int
    public var maxHops: Int
    public var hitlRequired: Bool
    public var hitlApproved: Bool?
    public var hitlFeedback: String?

    // Final Outputs & Trace
    public var finalPlan: [StudySession]
    public var finalSummary: String
    public var trace: [AgentTraceEvent]
    public var isTerminated: Bool
    public var terminationReason: String?

    public init(
        query: String = "",
        studentId: String = "student_001",
        subject: String = "Computer Science",
        topicsCovered: Int = 0,
        totalTopics: Int = 20,
        daysLeft: Int = 7,
        hoursPerTopic: Double = 2.0,
        staminaHoursPerDay: Double = 4.0,
        readinessScore: Double? = nil,
        isReady: Bool? = nil,
        readinessAssessment: String? = nil,
        ragSnippets: [String] = [],
        calculatedHoursPerDay: Double? = nil,
        negotiatedHoursPerDay: Double? = nil,
        isOverStamina: Bool = false,
        planProposal: String? = nil,
        hopCount: Int = 0,
        maxHops: Int = 5,
        hitlRequired: Bool = false,
        hitlApproved: Bool? = nil,
        hitlFeedback: String? = nil,
        finalPlan: [StudySession] = [],
        finalSummary: String = "",
        trace: [AgentTraceEvent] = [],
        isTerminated: Bool = false,
        terminationReason: String? = nil
    ) {
        self.query = query
        self.studentId = studentId
        self.subject = subject
        self.topicsCovered = topicsCovered
        self.totalTopics = totalTopics
        self.daysLeft = daysLeft
        self.hoursPerTopic = hoursPerTopic
        self.staminaHoursPerDay = staminaHoursPerDay
        self.readinessScore = readinessScore
        self.isReady = isReady
        self.readinessAssessment = readinessAssessment
        self.ragSnippets = ragSnippets
        self.calculatedHoursPerDay = calculatedHoursPerDay
        self.negotiatedHoursPerDay = negotiatedHoursPerDay
        self.isOverStamina = isOverStamina
        self.planProposal = planProposal
        self.hopCount = hopCount
        self.maxHops = maxHops
        self.hitlRequired = hitlRequired
        self.hitlApproved = hitlApproved
        self.hitlFeedback = hitlFeedback
        self.finalPlan = finalPlan
        self.finalSummary = finalSummary
        self.trace = trace
        self.isTerminated = isTerminated
        self.terminationReason = terminationReason
    }

    public mutating func appendTrace(
        agentName: String,
        stepType: AgentTraceEvent.StepType,
        title: String,
        detail: String,
        isWarningOrError: Bool = false
    ) {
        let event = AgentTraceEvent(
            hopIndex: self.hopCount,
            agentName: agentName,
            stepType: stepType,
            title: title,
            detail: detail,
            isWarningOrError: isWarningOrError
        )
        self.trace.append(event)
    }
}
