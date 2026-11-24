import SwiftUI

/// Chapter 1 ReAct & Chapter 4 Multi-Agent Trace Viewer
public struct TraceView: View {
    @State private var sampleScenario: String = "TC3: Urgent Crunch (Charlie)"
    @State private var traceEvents: [AgentTraceEvent] = []
    @State private var selectedFilter: String = "All"

    private let scenarios = [
        "TC1: Fully Prepared (Alice)",
        "TC2: Borderline (Bob)",
        "TC3: Urgent Crunch (Charlie)",
        "TC4: Extreme Overload",
        "TC5: Zero Days Left"
    ]

    public init() {}

    public var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Scenario Selector Bar
                VStack(spacing: 10) {
                    Picker("Benchmark Scenario", selection: $sampleScenario) {
                        ForEach(scenarios, id: \.self) { sc in
                            Text(sc).tag(sc)
                        }
                    }
                    .pickerStyle(.menu)
                    .padding(.horizontal)

                    Button(action: runBenchmarkScenario) {
                        HStack {
                            Image(systemName: "play.circle.fill")
                            Text("Execute Scenario & Stream ReAct Trace")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(Color.indigo)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 12)
                .background(AppTheme.cardBackground)

                // Trace Timeline List
                if traceEvents.isEmpty {
                    VStack(spacing: 12) {
                        Spacer()
                        Image(systemName: "waveform.path.ecg")
                            .font(.system(size: 48))
                            .foregroundColor(.secondary)
                        Text("No active trace. Tap 'Execute Scenario' above to watch multi-agent ReAct hops.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 40)
                        Spacer()
                    }
                } else {
                    List {
                        ForEach(traceEvents) { event in
                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    Text("Hop #\(event.hopIndex)")
                                        .font(.caption2.bold())
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(Color.gray.opacity(0.2))
                                        .cornerRadius(4)

                                    badgeForAgent(event.agentName)

                                    Spacer()

                                    Text(event.stepType.rawValue)
                                        .font(.caption2.bold())
                                        .foregroundColor(colorForStep(event.stepType))
                                }

                                Text(event.title)
                                    .font(.headline)
                                    .foregroundColor(event.isWarningOrError ? .orange : .primary)

                                Text(event.detail)
                                    .font(.footnote)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("ReAct Trace Explorer")
            .onAppear {
                if traceEvents.isEmpty {
                    runBenchmarkScenario()
                }
            }
        }
    }

    private func badgeForAgent(_ name: String) -> some View {
        let color: Color = {
            if name.contains("Supervisor") { return .purple }
            if name.contains("Diagnostician") { return .blue }
            if name.contains("Workload") { return .green }
            return .orange
        }()

        return Text(name)
            .font(.caption.bold())
            .padding(.horizontal, 8)
            .padding(.vertical, 2)
            .background(color.opacity(0.15))
            .foregroundColor(color)
            .cornerRadius(6)
    }

    private func colorForStep(_ step: AgentTraceEvent.StepType) -> Color {
        switch step {
        case .thought: return .blue
        case .action: return .purple
        case .observation: return .green
        case .guardrailBlock: return .red
        case .hitlPrompt, .hitlDecision: return .orange
        case .synthesis: return .indigo
        }
    }

    private func runBenchmarkScenario() {
        var state: AgentState

        if sampleScenario.contains("TC1") {
            state = AgentState(
                query: "Assess readiness: 20/20 topics covered, 5 days left",
                studentId: "student_alice",
                topicsCovered: 20,
                totalTopics: 20,
                daysLeft: 5,
                hoursPerTopic: 2.0
            )
        } else if sampleScenario.contains("TC2") {
            state = AgentState(
                query: "Assess readiness: 16/20 topics covered, 4 days left",
                studentId: "student_bob",
                topicsCovered: 16,
                totalTopics: 20,
                daysLeft: 4,
                hoursPerTopic: 1.5
            )
        } else if sampleScenario.contains("TC3") {
            state = AgentState(
                query: "Assess readiness: 5/12 topics covered, 2 days left",
                studentId: "student_charlie",
                topicsCovered: 5,
                totalTopics: 12,
                daysLeft: 2,
                hoursPerTopic: 1.5
            )
        } else if sampleScenario.contains("TC4") {
            state = AgentState(
                query: "Assess readiness: 2/20 topics covered, 1 day left",
                studentId: "student_charlie",
                topicsCovered: 2,
                totalTopics: 20,
                daysLeft: 1,
                hoursPerTopic: 2.5
            )
        } else {
            // TC5 Zero days
            state = AgentState(
                query: "Assess readiness: 10/20 topics covered, 0 days left",
                studentId: "student_bob",
                topicsCovered: 10,
                totalTopics: 20,
                daysLeft: 0,
                hoursPerTopic: 2.0
            )
        }

        SupervisorAgent.process(state: &state, autoApproveHITL: true)
        self.traceEvents = state.trace
    }
}
