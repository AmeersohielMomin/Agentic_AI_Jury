import Foundation

/// Layer 1 Safety Guardrail: Detects adversarial prompt injections and redacts sensitive PII (Unit 5)
public struct InputGuard: Sendable {
    public struct ValidationResult: Sendable, Equatable {
        public let isSafe: Bool
        public let sanitizedText: String
        public let detectedViolations: [String]
        public let refusalReason: String?
    }

    // High-risk prompt injection patterns (matching Unit 5 coursework)
    private static let injectionPatterns: [String] = [
        "(?i)ignore\\s+(all\\s+)?previous\\s+instructions",
        "(?i)disregard\\s+(all\\s+)?prior\\s+guidelines",
        "(?i)system\\s+override",
        "(?i)jailbreak",
        "(?i)you\\s+are\\s+now\\s+in\\s+developer\\s+mode",
        "(?i)act\\s+as\\s+an\\s+unconstrained\\s+ai",
        "(?i)bypass\\s+guardrails?",
        "(?i)prescribe\\s+.*\\b(oxycodone|fentanyl|morphine)\\b",
        "(?i)sudo\\s+mode"
    ]

    // PII patterns (Aadhaar/National ID, 10-digit Phone numbers, Emails)
    private static let nationalIdPattern = "\\b[0-9]{4}\\s?[0-9]{4}\\s?[0-9]{4}\\b"
    private static let phonePattern = "\\b[6-9][0-9]{9}\\b"
    private static let emailPattern = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"

    public static func validate(input: String) -> ValidationResult {
        var violations: [String] = []

        // 1. Scan for adversarial injection patterns
        for pattern in injectionPatterns {
            if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                let range = NSRange(location: 0, length: input.utf16.count)
                if regex.firstMatch(in: input, options: [], range: range) != nil {
                    violations.append("Adversarial Prompt Injection detected: '\(pattern)'")
                }
            }
        }

        if !violations.isEmpty {
            let reason = "SECURITY REFUSAL: Input violates Agentic Safety Policy. Pattern matching adversarial prompt injection detected."
            return ValidationResult(
                isSafe: false,
                sanitizedText: "[REFUSED_ADVERSARIAL_INPUT]",
                detectedViolations: violations,
                refusalReason: reason
            )
        }

        // 2. Redact PII (Privacy preserving on-device)
        var sanitized = input

        // Redact National IDs
        if let regex = try? NSRegularExpression(pattern: nationalIdPattern, options: []) {
            let range = NSRange(location: 0, length: sanitized.utf16.count)
            sanitized = regex.stringByReplacingMatches(in: sanitized, options: [], range: range, withTemplate: "[REDACTED_ID]")
        }

        // Redact Phones
        if let regex = try? NSRegularExpression(pattern: phonePattern, options: []) {
            let range = NSRange(location: 0, length: sanitized.utf16.count)
            sanitized = regex.stringByReplacingMatches(in: sanitized, options: [], range: range, withTemplate: "[REDACTED_PHONE]")
        }

        // Redact Emails
        if let regex = try? NSRegularExpression(pattern: emailPattern, options: []) {
            let range = NSRange(location: 0, length: sanitized.utf16.count)
            sanitized = regex.stringByReplacingMatches(in: sanitized, options: [], range: range, withTemplate: "[REDACTED_EMAIL]")
        }

        return ValidationResult(
            isSafe: true,
            sanitizedText: sanitized,
            detectedViolations: [],
            refusalReason: nil
        )
    }
}
