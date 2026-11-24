import SwiftUI

/// Main Root TabView Container for StudyMind AI
public struct ContentView: View {
    public init() {}

    public var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "square.grid.2x2.fill")
                }

            TraceView()
                .tabItem {
                    Label("ReAct Trace", systemImage: "waveform.path.ecg")
                }

            GuardrailLogView()
                .tabItem {
                    Label("Guardrails", systemImage: "shield.checkered")
                }

            SyllabusImportView()
                .tabItem {
                    Label("Syllabus RAG", systemImage: "book.pages.fill")
                }

            ProfileView()
                .tabItem {
                    Label("Profiles", systemImage: "person.crop.circle.fill")
                }
        }
    }
}

#Preview {
    ContentView()
}
