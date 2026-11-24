import SwiftUI

/// Chapter 3-2: Long-Term Memory Profile Manager View
public struct ProfileView: View {
    @State private var profiles: [StudentProfile] = []
    @State private var newName: String = ""
    @State private var newSubject: String = "Agentic AI"
    @State private var newStamina: Double = 4.0

    public init() {}

    public var body: some View {
        NavigationStack {
            List {
                Section(header: Text("Stored Student Profiles (SQLite / Disk)")) {
                    ForEach(profiles) { profile in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(profile.name)
                                    .font(.headline)
                                Spacer()
                                Text("\(String(format: "%.1f", profile.staminaHoursPerDay)) h/day cap")
                                    .font(.caption.bold())
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 2)
                                    .background(Color.blue.opacity(0.15))
                                    .foregroundColor(.blue)
                                    .cornerRadius(6)
                            }

                            Text("Subject: \(profile.targetSubject)")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            if !profile.historicalScores.isEmpty {
                                HStack {
                                    Text("Past Exam Scores:")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text(profile.historicalScores.map { "\(Int($0))%" }.joined(separator: ", "))
                                        .font(.caption.bold())
                                }
                            }

                            Text(profile.notes)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                }

                Section(header: Text("Add Custom Profile")) {
                    TextField("Student Name", text: $newName)
                    TextField("Target Subject", text: $newSubject)
                    HStack {
                        Text("Daily Stamina Cap:")
                        Spacer()
                        Text("\(String(format: "%.1f", newStamina)) hours")
                            .fontWeight(.semibold)
                    }
                    Slider(value: $newStamina, in: 2.0...8.0, step: 0.5)

                    Button("Save Profile to Long-Term Memory") {
                        saveNewProfile()
                    }
                    .disabled(newName.isEmpty)
                }

                Section(footer: Text("Profiles are persisted to disk using Atomic JSON/SQLite-compatible storage, surviving app terminations.")) {
                    EmptyView()
                }
            }
            .navigationTitle("Student Profiles")
            .onAppear {
                loadProfiles()
            }
        }
    }

    private func loadProfiles() {
        profiles = StudentProfileStore.shared.listAllProfiles()
    }

    private func saveNewProfile() {
        let newId = "student_\(UUID().uuidString.prefix(6))"
        let p = StudentProfile(
            studentId: newId,
            name: newName,
            targetSubject: newSubject,
            staminaHoursPerDay: newStamina,
            historicalScores: [70.0],
            notes: "Created via StudyMind AI iOS Profile Manager."
        )
        StudentProfileStore.shared.saveProfile(p)
        newName = ""
        loadProfiles()
    }
}
