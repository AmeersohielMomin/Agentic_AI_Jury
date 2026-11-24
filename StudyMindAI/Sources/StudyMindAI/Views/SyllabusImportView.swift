import SwiftUI

/// Chapter 3-3: On-Device Syllabus Guidelines & RAG Query Inspector
public struct SyllabusImportView: View {
    @State private var searchQuery: String = "What is the passing readiness benchmark?"
    @State private var searchResult: String = ""
    @State private var isGroundedRefusal: Bool = false
    @State private var newTopic: String = ""
    @State private var newContent: String = ""

    public init() {}

    public var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Semantic Query Box
                    VStack(alignment: .leading, spacing: 12) {
                        Text("On-Device Syllabus RAG Retrieval")
                            .font(.headline)
                        Text("Queries syllabus guidelines using local keyword & TF-IDF semantic matching with strict grounded refusal.")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        TextField("Enter query about course guidelines...", text: $searchQuery)
                            .padding()
                            .background(AppTheme.nestedBackground)
                            .cornerRadius(10)

                        HStack {
                            Button(action: runSearch) {
                                HStack {
                                    Image(systemName: "magnifyingglass")
                                    Text("Retrieve Guidelines")
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 16)
                                .padding(.vertical, 10)
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                            }
                            Spacer()
                        }

                        // Presets
                        HStack(spacing: 8) {
                            presetButton("Benchmark?") { searchQuery = "readiness benchmark threshold" }
                            presetButton("Fatigue limits?") { searchQuery = "daily study workload fatigue limits" }
                            presetButton("Out of Scope?") { searchQuery = "what is the campus cafeteria menu?" }
                        }

                        // Search Result Display
                        if !searchResult.isEmpty {
                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    Image(systemName: isGroundedRefusal ? "exclamationmark.octagon.fill" : "doc.text.magnifyingglass")
                                        .foregroundColor(isGroundedRefusal ? .orange : .blue)
                                    Text(isGroundedRefusal ? "Grounded Refusal Active" : "Verified RAG Match")
                                        .font(.subheadline.bold())
                                        .foregroundColor(isGroundedRefusal ? .orange : .blue)
                                }

                                Text(searchResult)
                                    .font(.footnote)
                                    .foregroundColor(.primary)
                            }
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(isGroundedRefusal ? Color.orange.opacity(0.15) : Color.blue.opacity(0.1))
                            .cornerRadius(10)
                        }
                    }
                    .padding()
                    .background(AppTheme.cardBackground)
                    .cornerRadius(16)

                    // Add custom chunk
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Add Custom Syllabus Note")
                            .font(.headline)

                        TextField("Topic Title (e.g. Unit 5 Practice)", text: $newTopic)
                            .padding(10)
                            .background(AppTheme.nestedBackground)
                            .cornerRadius(8)

                        TextField("Guideline Content / Exam Tips", text: $newContent)
                            .padding(10)
                            .background(AppTheme.nestedBackground)
                            .cornerRadius(8)

                        Button("Index Note into RAG Corpus") {
                            guard !newTopic.isEmpty && !newContent.isEmpty else { return }
                            let chunk = SyllabusChunk(
                                id: "KB_\(UUID().uuidString.prefix(4))",
                                subject: "Agentic AI",
                                topic: newTopic,
                                section: "Student Notes",
                                content: newContent,
                                recommendedHours: 2.0,
                                keywords: newTopic.lowercased().components(separatedBy: " ")
                            )
                            RAGTool.shared.addSyllabusChunks([chunk])
                            newTopic = ""
                            newContent = ""
                            searchResult = "Successfully indexed into local RAG corpus!"
                            isGroundedRefusal = false
                        }
                        .fontWeight(.semibold)
                        .padding(.vertical, 8)
                    }
                    .padding()
                    .background(AppTheme.cardBackground)
                    .cornerRadius(16)
                }
                .padding()
            }
            .navigationTitle("Syllabus RAG")
            .onAppear {
                runSearch()
            }
        }
    }

    private func presetButton(_ title: String, action: @escaping () -> Void) -> some View {
        Button(action: {
            action()
            runSearch()
        }) {
            Text(title)
                .font(.caption2.bold())
                .padding(.horizontal, 8)
                .padding(.vertical, 6)
                .background(Color.gray.opacity(0.15))
                .foregroundColor(.primary)
                .cornerRadius(6)
        }
    }

    private func runSearch() {
        guard !searchQuery.isEmpty else { return }
        let (_, isRefusal, response) = RAGTool.shared.retrieve(query: searchQuery, topK: 2)
        self.isGroundedRefusal = isRefusal
        self.searchResult = response
    }
}
