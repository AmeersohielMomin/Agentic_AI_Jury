import Foundation

/// Specialist Agent 2: Workload Planner & Negotiator (Unit 4-1 Spec)
/// Computes required daily hours, checks against student fatigue limits, and negotiates realistic pacing.
public struct WorkloadPlannerAgent: Sendable {
    public static let agentName = "Workload Planner"

    public static func execute(state: inout AgentState) {
        state.hopCount += 1

        // 1. Check Long-Term Memory for Student Profile (Unit 3-2)
        if let profile = StudentProfileStore.shared.getProfile(studentId: state.studentId) {
            state.staminaHoursPerDay = profile.staminaHoursPerDay
            state.appendTrace(
                agentName: agentName,
                stepType: .thought,
                title: "Recalled Student Profile from SQLite",
                detail: "Retrieved profile for '\(profile.name)': Stamina cap = \(profile.staminaHoursPerDay)h/day. Historical avg = \(profile.historicalScores.isEmpty ? 0 : profile.historicalScores.reduce(0, +) / Double(profile.historicalScores.count))%."
            )
        }

        // 2. Defensive check for Zero Days Boundary (TC5 Scenario)
        if state.daysLeft == 0 {
            state.appendTrace(
                agentName: agentName,
                stepType: .thought,
                title: "Boundary Condition Detected: 0 Days Left",
                detail: "Exam is today. Normal multi-day division is invalid. Executing zero-day recovery protocol."
            )

            state.calculatedHoursPerDay = 0.0
            state.negotiatedHoursPerDay = 0.0
            state.isOverStamina = false
            state.planProposal = "EMERGENCY PROTOCOL: Exam is today (0 days left). Bypass multi-day schedule. Dedicate 2 hours to quick summary review and formula sheet review."

            state.appendTrace(
                agentName: agentName,
                stepType: .observation,
                title: "Zero-Day Plan Synthesized",
                detail: state.planProposal ?? ""
            )

            state.finalPlan = [
                StudySession(dayIndex: 0, topicName: "Core Formula & Summary Triage", allocatedHours: 2.0, difficultyTag: "Urgent")
            ]
            return
        }

        // 3. ReAct Thought: Calculating Hours
        state.appendTrace(
            agentName: agentName,
            stepType: .thought,
            title: "Evaluating Workload Requirements",
            detail: "Remaining topics: \(state.totalTopics - state.topicsCovered), Days remaining: \(state.daysLeft), Estimated hours/topic: \(state.hoursPerTopic)h."
        )

        // 4. ReAct Action: Hours Calculator Tool Call
        state.appendTrace(
            agentName: agentName,
            stepType: .action,
            title: "Invoking hours_needed_per_day",
            detail: "Calling HoursCalculatorTool.calculate(covered: \(state.topicsCovered), total: \(state.totalTopics), days: \(state.daysLeft), hoursPerTopic: \(state.hoursPerTopic))"
        )

        let calcResult = HoursCalculatorTool.calculate(
            topicsCovered: state.topicsCovered,
            totalTopics: state.totalTopics,
            daysLeft: state.daysLeft,
            hoursPerTopic: state.hoursPerTopic
        )

        switch calcResult {
        case .success(let res):
            state.calculatedHoursPerDay = res.hoursPerDay

            // Check ToolCallGuard on workload ceiling (Unit 5)
            let guardCheck = ToolCallGuard.validateProposedWorkload(hoursPerDay: res.hoursPerDay)
            if !guardCheck.allowed {
                // TC4 Scenario: Extreme Overload (> 16h/day)
                state.isOverStamina = true
                state.negotiatedHoursPerDay = min(state.staminaHoursPerDay, 8.0)
                state.planProposal = "UNFEASIBLE WORKLOAD REJECTION: Calculated requirement is \(String(format: "%.1f", res.hoursPerDay))h/day. This exceeds human capacity. Schedule rejected; recommend institutional exam postponement or syllabus triage."

                state.appendTrace(
                    agentName: agentName,
                    stepType: .guardrailBlock,
                    title: "Extreme Overload Blocked by ToolCallGuard",
                    detail: guardCheck.reason ?? "Exceeds physical limits.",
                    isWarningOrError: true
                )
                return
            }

            // Check Peer Negotiation against Student Stamina (TC3 Scenario)
            if res.hoursPerDay > state.staminaHoursPerDay {
                state.isOverStamina = true
                state.negotiatedHoursPerDay = state.staminaHoursPerDay
                state.hitlRequired = true

                let negotiationDetail = "Calculated pace of \(String(format: "%.2f", res.hoursPerDay))h/day exceeds student stamina limit (\(state.staminaHoursPerDay)h/day). COUNTER-PROPOSAL: Cap schedule at \(state.staminaHoursPerDay)h/day to prevent burnout and trigger Human-in-the-Loop approval."
                state.planProposal = negotiationDetail

                state.appendTrace(
                    agentName: agentName,
                    stepType: .observation,
                    title: "Counter-Bid Triggered: Workload vs Stamina",
                    detail: negotiationDetail,
                    isWarningOrError: true
                )
            } else {
                state.isOverStamina = false
                state.negotiatedHoursPerDay = res.hoursPerDay
                state.planProposal = "Workload of \(String(format: "%.2f", res.hoursPerDay))h/day is within student stamina limit of \(state.staminaHoursPerDay)h/day. Schedule feasible."

                state.appendTrace(
                    agentName: agentName,
                    stepType: .observation,
                    title: "Schedule Feasible",
                    detail: state.planProposal ?? ""
                )
            }

            // Generate structured daily sessions
            let dailyHours = state.negotiatedHoursPerDay ?? res.hoursPerDay
            var sessions: [StudySession] = []
            for d in 1...state.daysLeft {
                sessions.append(StudySession(
                    dayIndex: d,
                    topicName: "Review Block \(d): Key Sub-Topics",
                    allocatedHours: dailyHours,
                    difficultyTag: dailyHours > 4.0 ? "Intensive" : "Standard"
                ))
            }
            state.finalPlan = sessions

        case .failure(let err):
            state.appendTrace(
                agentName: agentName,
                stepType: .observation,
                title: "Calculator Tool Error",
                detail: err.localizedDescription,
                isWarningOrError: true
            )
        }
    }
}
