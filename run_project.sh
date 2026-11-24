#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================================="
echo "  StudyMind AI — Multi-Agent On-Device iOS & Web Project Launcher"
echo "  PE-IV SEM-VII: Agentic AI | Ameersohiel N Momin (ADT23SOCB0116)"
echo "=================================================================="
echo ""
echo "Select execution mode:"
echo "  1) Run On-Device iOS Multi-Agent Benchmark (Swift CLI)"
echo "  2) Run iOS Unit & Benchmark Test Suite (XCTest)"
echo "  3) Launch Interactive Streamlit Web Dashboard"
echo "  4) Run All Verifications (Tests + Benchmarks + Web Dashboard)"
echo ""

read -p "Enter choice [1-4] (default: 1): " choice
choice=${choice:-1}

case "$choice" in
  1)
    echo ""
    echo "▶ Compiling and running StudyMindAICLI..."
    cd StudyMindAI && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift run StudyMindAICLI
    ;;
  2)
    echo ""
    echo "▶ Executing full XCTest benchmark test suite..."
    cd StudyMindAI && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test
    ;;
  3)
    echo ""
    echo "▶ Launching Web Dashboard on http://localhost:8501..."
    streamlit run web_dashboard/app.py
    ;;
  4)
    echo ""
    echo "▶ 1/3: Running XCTest Suite..."
    (cd StudyMindAI && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test)
    echo ""
    echo "▶ 2/3: Running iOS Multi-Agent Benchmark..."
    (cd StudyMindAI && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift run StudyMindAICLI)
    echo ""
    echo "▶ 3/3: Launching Web Dashboard..."
    streamlit run web_dashboard/app.py
    ;;
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac
