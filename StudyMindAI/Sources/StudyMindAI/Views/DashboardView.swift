import SwiftUI

/// Main Dashboard View: Interactive inputs, readiness score ring, and study schedule cards
public struct DashboardView: View {
    @State private var selectedStudentId: String = "student_bob"
    @State private var subjectName: String = "Agentic AI"
    @State private var topicsCovered: Double = 16
    @State private var totalTopics: Double = 20
    @State private var daysLeft: Double = 4
    @State private var hoursPerTopic: Double = 1.5

    @State private var currentState: AgentState?
    @State private var isOptimizing: Bool = false
    @State private var showHITLSheet: Bool = false

    private let presetStudents = [
        ("student_alice", "Alice (High Stamina: 6h)"),
        ("student_bob", "Bob (Cramming: 8h)"),
        ("student_charlie", "Charlie (Part-time: 3.5h)")
    ]

    public init() {}

    public var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // 1. Header & Student Profile Selection
                    VStack(alignment: .leading, spacing: 8) {
                        Text("StudyMind AI")
                            .font(.largeTitle.bold())
                        Text("On-Device Autonomous Multi-Agent Study Coach")
                            .font(.subheadline)
                            .foregroundColor(.secondary)

                        Picker("Student Profile", selection: $selectedStudentId) {
                            ForEach(presetStudents, id: \.0) { student in
                                Text(student.1).tag(student.0)
                            }
                        }
                        .pickerStyle(.segmented)
                        .padding(.top, 4)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(AppTheme.cardBackground)
                    .cornerRadius(16)

                    // 2. Readiness Ring & Metric Overview
                    if let state = currentState {
                        readinessOverviewCard(state: state)
                    }

                    // 3. Input Controls Card
                    VStack(alignment: .leading, spacing: 14) {
                        Text("Curriculum & Horizon Parameters")
                            .font(.headline)

                        HStack {
                            Text("Topics Covered:")
                            Spacer()
                            Text("\(Int(topicsCovered)) / \(Int(totalTopics))")
                                .fontWeight(.semibold)
                        }
                        Slider(value: $topicsCovered, in: 0...totalTopics, step: 1)

                        HStack {
                            Text("Days Until Exam:")
                            Spacer()
                            Text("\(Int(daysLeft)) days")
                                .fontWeight(.semibold)
                        }
                        Slider(value: $daysLeft, in: 0...14, step: 1)

                        HStack {
                            Text("Hours Per Topic:")
                            Spacer()
                            Text("\(String(format: "%.1f", hoursPerTopic))h")
                                .fontWeight(.semibold)
                        }
                        Slider(value: $hoursPerTopic, in: 0.5...4.0, step: 0.5)

                        // Run Agent Button
                        Button(action: runOptimization) {
                            HStack {
                                Image(systemName: "bolt.horizontal.circle.fill")
                                Text(isOptimizing ? "Agents Negotiating..." : "Run Multi-Agent Optimizer")
                                    .fontWeight(.bold)
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(isOptimizing)
                    }
                    .padding()
                    .background(AppTheme.cardBackground)
                    .cornerRadius(16)

                    // 4. Generated Study Sessions
                    if let state = currentState, !state.finalPlan.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Synthesized Study Schedule")
                                .font(.headline)

                            ForEach(state.finalPlan) { session in
                                HStack {
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text("Day \(session.dayIndex): \(session.topicName)")
                                            .fontWeight(.semibold)
                                        Text("Allocated: \(String(format: "%.1f", session.allocatedHours)) hours")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                    Spacer()
                                    Text(session.difficultyTag)
                                        .font(.caption.bold())
                                        .padding(.horizontal, 10)
                                        .padding(.vertical, 4)
                                        .background(session.difficultyTag == "Urgent" ? Color.red.opacity(0.2) : Color.blue.opacity(0.15))
                                        .foregroundColor(session.difficultyTag == "Urgent" ? .red : .blue)
                                        .cornerRadius(8)
                                }
                                .padding()
                                .background(AppTheme.nestedBackground)
                                .cornerRadius(12)
                            }
                        }
                        .padding()
                        .background(AppTheme.cardBackground)
                        .cornerRadius(16)
                    }
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .sheet(isPresented: $showHITLSheet) {
                if let state = currentState {
                    HITLApprovalView(
                        state: state,
                        onApprove: {
                            var approvedState = state
                            approvedState.hitlApproved = true
                            SupervisorAgent.process(state: &approvedState, autoApproveHITL: false)
                            currentState = approvedState
                            showHITLSheet = false
                        },
                        onReject: {
                            var rejectedState = state
                            rejectedState.hitlApproved = false
                            SupervisorAgent.process(state: &rejectedState, autoApproveHITL: false)
                            currentState = rejectedState
                            showHITLSheet = false
                        }
                    )
                }
            }
        }
    }

    private func readinessOverviewCard(state: AgentState) -> some View {
        HStack(spacing: 20) {
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.2), lineWidth: 10)
                    .frame(width: 90, height: 90)

                let percentage = state.readinessScore ?? 0
                Circle()
                    .trim(from: 0, to: CGFloat(min(percentage / 100.0, 1.0)))
                    .stroke(percentage >= 80 ? Color.green : Color.orange, style: StrokeStyle(lineWidth: 10, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .frame(width: 90, height: 90)

                VStack(spacing: 2) {
                    Text("\(Int(percentage))%")
                        .font(.title3.bold())
                    Text(percentage >= 80 ? "READY" : "REVIEW")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(percentage >= 80 ? .green : .orange)
                }
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(state.isReady == true ? "Exam Readiness Met" : "Readiness Gap Detected")
                    .font(.headline)
                    .foregroundColor(state.isReady == true ? .green : .orange)

                if let calc = state.calculatedHoursPerDay {
                    Text("Required Pace: **\(String(format: "%.1f", calc))h / day**")
                        .font(.subheadline)
                }

                if state.isOverStamina {
                    HStack(spacing: 4) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.red)
                        Text("Burnout Guard Triggered!")
                            .font(.caption.bold())
                            .foregroundColor(.red)
                    }
                }
            }
            Spacer()
        }
        .padding()
        .background(AppTheme.cardBackground)
        .cornerRadius(16)
    }

    private func runOptimization() {
        isOptimizing = true

        var state = AgentState(
            query: "Plan optimal study schedule for \(subjectName)",
            studentId: selectedStudentId,
            subject: subjectName,
            topicsCovered: Int(topicsCovered),
            totalTopics: Int(totalTopics),
            daysLeft: Int(daysLeft),
            hoursPerTopic: hoursPerTopic
        )

        SupervisorAgent.process(state: &state, autoApproveHITL: false)
        currentState = state
        isOptimizing = false

        if state.hitlRequired && state.hitlApproved == nil {
            showHITLSheet = true
        }
    }
}
