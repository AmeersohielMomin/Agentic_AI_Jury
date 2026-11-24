import Foundation

/// Specialist Agent 1: Readiness Diagnostician (Unit 4-1 Spec)
/// Evaluates syllabus coverage against the 80% benchmark and queries course guidelines via RAG.
public struct DiagnosticianAgent: Sendable {
    public static let agentName = "Readiness Diagnostician"

    public static func execute(state: inout AgentState) {
        state.hopCount += 1

        // 1. ReAct Thought
        state.appendTrace(
            agentName: agentName,
            stepType: .thought,
            title: "Diagnosing Exam Readiness",
            detail: "Analyzing syllabus completion for '\(state.subject)': \(state.topicsCovered)/\(state.totalTopics) topics completed. Querying RAG guidelines."
        )

        // 2. ReAct Action: Check Readiness Tool
        state.appendTrace(
            agentName: agentName,
            stepType: .action,
            title: "Invoking check_exam_readiness",
            detail: "Calling ExamReadinessTool.evaluate(topicsCovered: \(state.topicsCovered), totalTopics: \(state.totalTopics))"
        )

        let readinessResult = ExamReadinessTool.evaluate(
            topicsCovered: state.topicsCovered,
            totalTopics: state.totalTopics
        )

        switch readinessResult {
        case .success(let res):
            state.readinessScore = res.percentage
            state.isReady = res.isReady
            state.readinessAssessment = res.message

            // ReAct Observation
            state.appendTrace(
                agentName: agentName,
                stepType: .observation,
                title: "Readiness Tool Result",
                detail: res.message
            )

        case .failure(let err):
            state.readinessAssessment = "Error assessing readiness: \(err.localizedDescription)"
            state.appendTrace(
                agentName: agentName,
                stepType: .observation,
                title: "Tool Error Encountered",
                detail: err.localizedDescription,
                isWarningOrError: true
            )
        }

        // 3. RAG Retrieval for Subject Guidelines (Unit 3-3)
        let ragResponse = RAGTool.shared.retrieve(query: "readiness benchmark for \(state.subject)", topK: 1)
        if !ragResponse.groundedRefusal {
            state.ragSnippets = ragResponse.results.map { $0.content }
            state.appendTrace(
                agentName: agentName,
                stepType: .observation,
                title: "RAG Guidelines Retrieved",
                detail: ragResponse.response
            )
        }
    }
}
