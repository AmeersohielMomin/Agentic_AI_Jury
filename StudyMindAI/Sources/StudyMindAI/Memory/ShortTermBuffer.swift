import Foundation

/// In-Memory Thread-Based Short-Term Context Buffer (Unit 3-1)
public final class ShortTermBuffer: @unchecked Sendable {
    public struct ContextEntry: Codable, Identifiable, Sendable, Equatable {
        public var id: UUID
        public var role: String // "user", "agent", "system"
        public var content: String
        public var timestamp: Date

        public init(id: UUID = UUID(), role: String, content: String, timestamp: Date = Date()) {
            self.id = id
            self.role = role
            self.content = content
            self.timestamp = timestamp
        }
    }

    private let maxCapacity: Int
    private var entries: [ContextEntry] = []
    private let lock = NSLock()

    public init(maxCapacity: Int = 10) {
        self.maxCapacity = maxCapacity
    }

    public func append(role: String, content: String) {
        lock.lock()
        defer { lock.unlock() }

        let entry = ContextEntry(role: role, content: content)
        entries.append(entry)

        // FIFO eviction if capacity exceeded
        if entries.count > maxCapacity {
            entries.removeFirst(entries.count - maxCapacity)
        }
    }

    public func getRecentEntries() -> [ContextEntry] {
        lock.lock()
        defer { lock.unlock() }
        return entries
    }

    public func getScratchpad() -> String {
        lock.lock()
        defer { lock.unlock() }
        return entries.map { "[\($0.role.uppercased())]: \($0.content)" }.joined(separator: "\n")
    }

    public func clear() {
        lock.lock()
        defer { lock.unlock() }
        entries.removeAll()
    }

    public var count: Int {
        lock.lock()
        defer { lock.unlock() }
        return entries.count
    }
}
