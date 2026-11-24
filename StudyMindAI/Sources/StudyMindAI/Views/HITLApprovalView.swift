import SwiftUI

/// Chapter 4-3: Human-in-the-Loop (HITL) Oversight Approval Sheet
public struct HITLApprovalView: View {
    public let state: AgentState
    public let onApprove: () -> Void
    public let onReject: () -> Void

    @State private var instructorFeedback: String = ""

    public init(state: AgentState, onApprove: @escaping () -> Void, onReject: @escaping () -> Void) {
        self.state = state
        self.onApprove = onApprove
        self.onReject = onReject
    }

    public var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Header Alert
                VStack(spacing: 8) {
                    Image(systemName: "person.crop.circle.badge.exclamationmark")
                        .font(.system(size: 50))
                        .foregroundColor(.orange)

                    Text("Human Oversight Gate Active")
                        .font(.title2.bold())

                    Text("The multi-agent system encountered a workload negotiation requiring human evaluator confirmation.")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top)

                // Comparison Box
                VStack(alignment: .leading, spacing: 14) {
                    Text("Negotiation Summary")
                        .font(.headline)

                    HStack {
                        VStack(alignment: .leading) {
                            Text("Calculated Math")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("\(String(format: "%.2f", state.calculatedHoursPerDay ?? 0)) h/day")
                                .font(.title3.bold())
                                .foregroundColor(.red)
                        }
                        Spacer()
                        Image(systemName: "arrow.right")
                            .foregroundColor(.secondary)
                        Spacer()
                        VStack(alignment: .trailing) {
                            Text("Student Stamina Cap")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("\(String(format: "%.2f", state.staminaHoursPerDay)) h/day")
                                .font(.title3.bold())
                                .foregroundColor(.blue)
                        }
                    }
                    .padding()
                    .background(AppTheme.nestedBackground)
                    .cornerRadius(12)

                    Text(state.planProposal ?? "Counter-proposal: Cap daily study at safe stamina limit to avoid burnout.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(AppTheme.cardBackground)
                .cornerRadius(16)
                .padding(.horizontal)

                Spacer()

                // Action Buttons
                VStack(spacing: 12) {
                    Button(action: onApprove) {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                            Text("Approve Counter-Bid (\(String(format: "%.1f", state.negotiatedHoursPerDay ?? state.staminaHoursPerDay))h/day)")
                                .fontWeight(.bold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }

                    Button(action: onReject) {
                        HStack {
                            Image(systemName: "xmark.circle")
                            Text("Reject & Request Syllabus Triage")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.red.opacity(0.15))
                        .foregroundColor(.red)
                        .cornerRadius(12)
                    }
                }
                .padding(.horizontal)
                .padding(.bottom)
            }
            .navigationTitle("Human Oversight")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
        }
    }
}
