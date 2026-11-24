import Foundation

/// Persistent Long-Term Memory Store for Student Profiles (Unit 3-2)
/// Survives application restarts and process terminations.
public final class StudentProfileStore: @unchecked Sendable {
    public static let shared = StudentProfileStore()

    private let storageURL: URL
    private let lock = NSLock()

    public init(storageURL: URL? = nil) {
        if let customURL = storageURL {
            self.storageURL = customURL
        } else {
            let fileManager = FileManager.default
            let paths = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask)
            let baseDir = paths.first ?? URL(fileURLWithPath: NSTemporaryDirectory())
            let appDir = baseDir.appendingPathComponent("StudyMindAI", isDirectory: true)

            try? fileManager.createDirectory(at: appDir, withIntermediateDirectories: true)
            self.storageURL = appDir.appendingPathComponent("student_profiles.json")
        }

        seedDefaultProfilesIfEmpty()
    }

    private func seedDefaultProfilesIfEmpty() {
        lock.lock()
        defer { lock.unlock() }

        if !FileManager.default.fileExists(atPath: storageURL.path) {
            let defaults = [
                StudentProfile(
                    studentId: "student_alice",
                    name: "Alice Johnson",
                    targetSubject: "Agentic AI",
                    staminaHoursPerDay: 6.0,
                    historicalScores: [88.0, 92.5],
                    notes: "High endurance student. Prepares consistently."
                ),
                StudentProfile(
                    studentId: "student_bob",
                    name: "Bob Martinez",
                    targetSubject: "Agentic AI",
                    staminaHoursPerDay: 8.0,
                    historicalScores: [75.0, 78.0],
                    notes: "Can handle intensive 8h cramming sessions safely."
                ),
                StudentProfile(
                    studentId: "student_charlie",
                    name: "Charlie Patel",
                    targetSubject: "Agentic AI",
                    staminaHoursPerDay: 3.5,
                    historicalScores: [62.0, 68.0],
                    notes: "Working student with part-time job. Strict 3.5h/day stamina limit."
                )
            ]
            saveProfilesInternal(defaults)
        }
    }

    private func loadProfilesInternal() -> [StudentProfile] {
        guard let data = try? Data(contentsOf: storageURL),
              let profiles = try? JSONDecoder().decode([StudentProfile].self, from: data) else {
            return []
        }
        return profiles
    }

    private func saveProfilesInternal(_ profiles: [StudentProfile]) {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        if let data = try? encoder.encode(profiles) {
            try? data.write(to: storageURL, options: .atomic)
        }
    }

    public func saveProfile(_ profile: StudentProfile) {
        lock.lock()
        defer { lock.unlock() }

        var profiles = loadProfilesInternal()
        if let index = profiles.firstIndex(where: { $0.studentId == profile.studentId }) {
            profiles[index] = profile
        } else {
            profiles.append(profile)
        }
        saveProfilesInternal(profiles)
    }

    public func getProfile(studentId: String) -> StudentProfile? {
        lock.lock()
        defer { lock.unlock() }

        let profiles = loadProfilesInternal()
        return profiles.first(where: { $0.studentId == studentId })
    }

    public func listAllProfiles() -> [StudentProfile] {
        lock.lock()
        defer { lock.unlock() }
        return loadProfilesInternal()
    }
}
