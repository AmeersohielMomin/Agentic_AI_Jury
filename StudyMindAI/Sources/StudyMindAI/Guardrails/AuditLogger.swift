import Foundation

/// Security and Operational Audit Logger for Multi-Agent Actions & Guardrails (Unit 5)
public final class AuditLogger: @unchecked Sendable {
    public static let shared = AuditLogger()

    public struct LogEntry: Codable, Identifiable, Sendable, Equatable {
        public var id: UUID
        public var timestamp: Date
        public var layer: String
        public var status: String // "PASSED", "WARNED", "BLOCKED"
        public var details: String

        public init(
            id: UUID = UUID(),
            timestamp: Date = Date(),
            layer: String,
            status: String,
            details: String
        ) {
            self.id = id
            self.timestamp = timestamp
            self.layer = layer
            self.status = status
            self.details = details
        }
    }

    private var logs: [LogEntry] = []
    private let lock = NSLock()

    public init() {}

    public func log(layer: String, status: String, details: String) {
        lock.lock()
        defer { lock.unlock() }

        let entry = LogEntry(layer: layer, status: status, details: details)
        logs.append(entry)
    }

    public func getRecentLogs(limit: Int = 50) -> [LogEntry] {
        lock.lock()
        defer { lock.unlock() }
        return Array(logs.suffix(limit))
    }

    public func clear() {
        lock.lock()
        defer { lock.unlock() }
        logs.removeAll()
    }
}
