import Foundation

/// On-Device Retrieval Augmented Generation (RAG) Tool for Course Guidelines (Unit 3-3)
public final class RAGTool: @unchecked Sendable {
    public static let shared = RAGTool()

    private var corpus: [SyllabusChunk] = []
    private let minimumRelevanceThreshold: Double = 0.25

    private static let stopWords: Set<String> = [
        "the", "what", "how", "why", "who", "when", "where", "and", "for", "with",
        "from", "that", "this", "are", "was", "were", "been", "has", "have", "had",
        "does", "did", "can", "could", "will", "would", "about", "lot"
    ]

    public init() {
        seedDefaultCorpus()
    }

    private func seedDefaultCorpus() {
        corpus = [
            SyllabusChunk(
                id: "KB_001",
                subject: "Agentic AI",
                topic: "Exam Readiness Benchmark",
                section: "Academic Policy",
                content: "Academic readiness threshold is strictly set at 80.0% syllabus coverage. Students reaching 80% or higher are classified as 'Ready' and should focus on revision and mock tests. Below 80%, prioritized topic remediation is required.",
                recommendedHours: 1.5,
                keywords: ["readiness", "benchmark", "threshold", "80%", "syllabus", "coverage", "ready", "pass"]
            ),
            SyllabusChunk(
                id: "KB_002",
                subject: "Agentic AI",
                topic: "Daily Workload & Cognitive Fatigue",
                section: "Health & Fatigue Policy",
                content: "Maximum sustainable daily study is capped at 6.0 hours for average students, and 8.0 hours under intensive cramming. Any schedule exceeding 8.0 hours/day induces severe cognitive fatigue, decreasing retention by over 40%. Extreme workloads above 12.0 hours are strictly biologically unfeasible.",
                recommendedHours: 2.0,
                keywords: ["stamina", "fatigue", "hours", "burnout", "limit", "biological", "ceiling", "cognitive", "daily"]
            ),
            SyllabusChunk(
                id: "KB_003",
                subject: "Agentic AI",
                topic: "Unit 2: Planning & ReAct Framework",
                section: "Core Curriculum",
                content: "Unit 2 covers Chain-of-Thought (CoT), Tree-of-Thoughts (ToT), and ReAct (Reason + Act). Focus areas include Thought-Action-Observation loops, in-place replanning upon tool failure, and maintaining deterministic tool interfaces.",
                recommendedHours: 3.5,
                keywords: ["unit 2", "react", "planning", "cot", "tot", "replanning", "thought", "action", "observation"]
            ),
            SyllabusChunk(
                id: "KB_004",
                subject: "Agentic AI",
                topic: "Unit 3: Memory & Deterministic Tools",
                section: "Core Curriculum",
                content: "Unit 3 covers Short-Term session context buffers, Long-Term SQLite profile persistence, Vector-based RAG retrieval with grounded refusal, and defensive tool error handling for boundary arithmetic.",
                recommendedHours: 3.0,
                keywords: ["unit 3", "memory", "short-term", "long-term", "sqlite", "rag", "chroma", "tools", "failure"]
            ),
            SyllabusChunk(
                id: "KB_005",
                subject: "Agentic AI",
                topic: "Unit 4: Multi-Agent Teams & Supervision",
                section: "Core Curriculum",
                content: "Unit 4 details role specifications (Goal, Tools, Inputs, Limits), supervisor routing with MAX_HOPS limits (typically 5), peer negotiation/counter-bidding, and Human-in-the-Loop (HITL) approval gates before action commitment.",
                recommendedHours: 4.0,
                keywords: ["unit 4", "multi-agent", "supervisor", "coordination", "max_hops", "hitl", "human-in-the-loop", "negotiation"]
            ),
            SyllabusChunk(
                id: "KB_006",
                subject: "Agentic AI",
                topic: "Unit 5: Domain Safety & Guardrails",
                section: "Core Curriculum",
                content: "Unit 5 emphasizes defense-in-depth: InputGuard for prompt injection and PII redaction, ToolCallGuard for parameter ceiling checks, OutputGuard for hallucination scrubbing, and immutable audit logging.",
                recommendedHours: 3.5,
                keywords: ["unit 5", "safety", "guardrails", "injection", "inputguard", "toolcallguard", "outputguard", "audit"]
            ),
            SyllabusChunk(
                id: "KB_007",
                subject: "Agentic AI",
                topic: "Zero Days Left Protocol",
                section: "Emergency Procedure",
                content: "When zero days remain prior to examination, dynamic multi-day scheduling is impossible. The student must bypass topic re-learning and immediately switch to 1-page formula summaries, past year paper reviews, and sleep management.",
                recommendedHours: 1.0,
                keywords: ["zero", "days", "emergency", "last minute", "crunch", "immediate", "summary"]
            ),
            SyllabusChunk(
                id: "KB_008",
                subject: "Agentic AI",
                topic: "Multi-Agent Counter-Bidding Protocol",
                section: "Scheduling Protocol",
                content: "When the Workload Planner calculates required hours exceeding the student's personal stamina, it must reject the unfeasible load and counter-propose a capped schedule matching student stamina, triggering human oversight for syllabus triage.",
                recommendedHours: 2.0,
                keywords: ["counter-bid", "negotiation", "stamina", "proposal", "oversight", "triage"]
            )
        ]
    }

    public func addSyllabusChunks(_ newChunks: [SyllabusChunk]) {
        self.corpus.append(contentsOf: newChunks)
    }

    public func retrieve(query: String, topK: Int = 2) -> (results: [SyllabusChunk], groundedRefusal: Bool, response: String) {
        let cleanedQuery = query.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        let queryTokens = Set(
            cleanedQuery
                .components(separatedBy: CharacterSet.alphanumerics.inverted)
                .filter { $0.count > 2 && !Self.stopWords.contains($0) }
        )

        guard !queryTokens.isEmpty else {
            let refusalText = "I don't know based on the provided documents. The queried topic is not present in the verified course guidelines."
            return ([], true, refusalText)
        }

        var scoredChunks: [(chunk: SyllabusChunk, score: Double)] = []

        for chunk in corpus {
            var score = 0.0
            let chunkText = (chunk.topic + " " + chunk.content + " " + chunk.keywords.joined(separator: " ")).lowercased()

            for token in queryTokens {
                if chunkText.contains(token) {
                    score += 1.0
                }
                if chunk.keywords.contains(where: { $0.lowercased() == token }) {
                    score += 1.5
                }
            }

            if score > 0 {
                let normalizedScore = score / Double(max(queryTokens.count, 1))
                scoredChunks.append((chunk, normalizedScore))
            }
        }

        scoredChunks.sort { $0.score > $1.score }

        let topMatches = scoredChunks.filter { $0.score >= minimumRelevanceThreshold }.prefix(topK).map { $0.chunk }

        if topMatches.isEmpty {
            // Grounded refusal matching Section 7 Q3 of TA2 report
            let refusalText = "I don't know based on the provided documents. The queried topic is not present in the verified course guidelines."
            return ([], true, refusalText)
        }

        let combinedSnippets = topMatches.map { "[\($0.section) - \($0.topic)]: \($0.content)" }.joined(separator: "\n\n")
        return (Array(topMatches), false, combinedSnippets)
    }
}
