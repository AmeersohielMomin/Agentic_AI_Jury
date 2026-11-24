import Foundation

/// Layer 3 Safety Guardrail: Sanitizes synthesized agent output before user delivery (Unit 5)
public struct OutputGuard: Sendable {
    public struct Result: Sendable, Equatable {
        public let isApproved: Bool
        public let cleanedOutput: String
        public let flaggedIssues: [String]
    }

    private static let dangerousMedicalKeywords = ["prescribe", "dosage", "oxycodone", "fentanyl", "milligrams", "mg orally"]

    public static func inspect(output: String) -> Result {
        var issues: [String] = []

        // Verify domain containment (e.g. out-of-domain drug prescription generation)
        let lower = output.lowercased()
        for kw in dangerousMedicalKeywords {
            if lower.contains(kw) {
                issues.append("Domain containment violation: Medical prescription terms detected in study schedule output.")
                break
            }
        }

        if !issues.isEmpty {
            return Result(
                isApproved: false,
                cleanedOutput: "BLOCKED: Generated content violated domain boundary constraints.",
                flaggedIssues: issues
            )
        }

        // Scrub any accidental raw prompt instructions or leakages
        var cleaned = output
        if cleaned.contains("SYSTEM PROMPT:") || cleaned.contains("<system>") {
            cleaned = cleaned.replacingOccurrences(of: "SYSTEM PROMPT:", with: "")
            cleaned = cleaned.replacingOccurrences(of: "<system>", with: "")
            cleaned = cleaned.replacingOccurrences(of: "</system>", with: "")
            issues.append("Stripped raw system prompt markers from output.")
        }

        return Result(isApproved: true, cleanedOutput: cleaned, flaggedIssues: issues)
    }
}
