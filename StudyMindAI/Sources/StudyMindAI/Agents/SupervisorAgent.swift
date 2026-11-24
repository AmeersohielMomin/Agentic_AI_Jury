import Foundation

/// Supervisor Orchestrator Agent (Unit 4-2 Spec)
/// Decomposes student requests, routes between specialists, enforces MAX_HOPS=5, and manages HITL gates.
public struct SupervisorAgent: Sendable {
    public static let supervisorName = "Supervisor Orchestrator"

    public static func process(state: inout AgentState, autoApproveHITL: Bool = false) {
        state.hopCount += 1

        // 1. Layer 1 Guardrail: Input Safety Check (Unit 5)
        let inputCheck = InputGuard.validate(input: state.query)
        if !inputCheck.isSafe {
            AuditLogger.shared.log(
                layer: "InputGuard",
                status: "BLOCKED",
                details: "Blocked query: '\(state.query)'. Violations: \(inputCheck.detectedViolations.joined(separator: ", "))"
            )

            state.appendTrace(
                agentName: supervisorName,
                stepType: .guardrailBlock,
                title: "Prompt Injection Attack Blocked",
                detail: inputCheck.refusalReason ?? "Input violates security policy.",
                isWarningOrError: true
            )

            state.isTerminated = true
            state.terminationReason = "Security refusal: Prompt injection detected."
            state.finalSummary = inputCheck.refusalReason ?? "Security refusal."
            return
        }

        AuditLogger.shared.log(
            layer: "InputGuard",
            status: "PASSED",
            details: "Sanitized query: '\(inputCheck.sanitizedText)'"
        )

        state.appendTrace(
            agentName: supervisorName,
            stepType: .thought,
            title: "Supervisor Pipeline Initialized",
            detail: "Request received for student '\(state.studentId)' on subject '\(state.subject)'. Enforcing hop ceiling MAX_HOPS = \(state.maxHops)."
        )

        // 2. Hop Ceiling Protection
        guard state.hopCount < state.maxHops else {
            state.isTerminated = true
            state.terminationReason = "MAX_HOPS (\(state.maxHops)) ceiling reached to prevent infinite negotiation loops."
            state.appendTrace(
                agentName: supervisorName,
                stepType: .observation,
                title: "Max Hops Exceeded",
                detail: state.terminationReason ?? "",
                isWarningOrError: true
            )
            return
        }

        // 3. Route 1: Readiness Diagnostician Specialist (Unit 4-1)
        state.appendTrace(
            agentName: supervisorName,
            stepType: .action,
            title: "Routing to Readiness Diagnostician",
            detail: "Dispatching state to DiagnosticianAgent to assess syllabus readiness threshold."
        )
        DiagnosticianAgent.execute(state: &state)

        // 4. Route 2: Workload Planner & Negotiator Specialist (Unit 4-1)
        state.appendTrace(
            agentName: supervisorName,
            stepType: .action,
            title: "Routing to Workload Planner",
            detail: "Dispatching state to WorkloadPlannerAgent to calculate pacing and check student stamina limits."
        )
        WorkloadPlannerAgent.execute(state: &state)

        // 5. Multi-Agent Consensus & Human Oversight Node (Unit 4-3)
        if state.hitlRequired {
            state.appendTrace(
                agentName: supervisorName,
                stepType: .hitlPrompt,
                title: "Human Oversight Requested (HITL Gate)",
                detail: "Proposed schedule requires \(String(format: "%.2f", state.calculatedHoursPerDay ?? 0))h/day vs student limit \(state.staminaHoursPerDay)h/day. Waiting for human approval of counter-bid.",
                isWarningOrError: true
            )

            if autoApproveHITL {
                state.hitlApproved = true
                state.appendTrace(
                    agentName: supervisorName,
                    stepType: .hitlDecision,
                    title: "Human Oversight: APPROVED",
                    detail: "Student/evaluator approved negotiated counter-proposal of \(state.negotiatedHoursPerDay ?? 0)h/day."
                )
            } else if state.hitlApproved == false {
                state.appendTrace(
                    agentName: supervisorName,
                    stepType: .hitlDecision,
                    title: "Human Oversight: REJECTED",
                    detail: "Student rejected plan. Replanning with syllabus triage.",
                    isWarningOrError: true
                )
            }
        }

        // 6. Synthesis and OutputGuard Inspection (Unit 5 Layer 3)
        let rawSummary = generateSynthesis(state: state)
        let outputCheck = OutputGuard.inspect(output: rawSummary)

        if outputCheck.isApproved {
            state.finalSummary = outputCheck.cleanedOutput
            AuditLogger.shared.log(layer: "OutputGuard", status: "PASSED", details: "Generated summary passed domain output inspection.")
        } else {
            state.finalSummary = "Output blocked by safety guardrails."
            AuditLogger.shared.log(layer: "OutputGuard", status: "BLOCKED", details: outputCheck.flaggedIssues.joined(separator: ", "))
        }

        state.appendTrace(
            agentName: supervisorName,
            stepType: .synthesis,
            title: "Schedule Plan Synthesized",
            detail: state.finalSummary
        )

        state.isTerminated = true
    }

    private static func generateSynthesis(state: AgentState) -> String {
        var lines: [String] = []

        let scoreStr = state.readinessScore != nil ? String(format: "%.1f", state.readinessScore!) : "N/A"
        let readyStatus = (state.isReady ?? false) ? "READY" : "NOT READY YET"

        lines.append("🎓 **Study Schedule Optimizer Summary**")
        lines.append("- **Subject:** \(state.subject)")
        lines.append("- **Readiness Status:** \(readyStatus) (\(scoreStr)% coverage)")

        if let calcHours = state.calculatedHoursPerDay {
            lines.append("- **Required Daily Study:** \(String(format: "%.2f", calcHours)) hours/day")
        }

        if let negHours = state.negotiatedHoursPerDay, negHours != state.calculatedHoursPerDay {
            lines.append("- **Negotiated Study Pace:** \(String(format: "%.2f", negHours)) hours/day (Burnout Protected)")
        }

        if let proposal = state.planProposal {
            lines.append("- **Agent Assessment:** \(proposal)")
        }

        if !state.ragSnippets.isEmpty {
            lines.append("\n📚 **Institutional Guidelines (Chroma RAG):**")
            for snippet in state.ragSnippets {
                lines.append("  • \(snippet)")
            }
        }

        if !state.finalPlan.isEmpty {
            lines.append("\n📅 **Schedule Allocations:**")
            for session in state.finalPlan {
                lines.append("  • Day \(session.dayIndex): \(session.topicName) — \(String(format: "%.1f", session.allocatedHours))h [\(session.difficultyTag)]")
            }
        }

        return lines.joined(separator: "\n")
    }
}
