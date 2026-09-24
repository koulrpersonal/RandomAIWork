"""
Convenience launcher for the Google ADK Web Interface.
Runs: adk web credit_policy_agent --port 8000
"""

import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_ADK = PROJECT_ROOT / "venv" / "Scripts" / "adk.exe"

def main():
    print("=" * 65)
    print("  LAUNCHING GOOGLE ADK WEB INTERFACE")
    print("  Apex Bank Australia — Credit Policy RAG Assistant")
    print("=" * 65)
    print("Starting local agent server on: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server.\n")

    cmd = [
        str(VENV_ADK) if VENV_ADK.exists() else "adk",
        "web",
        "credit_policy_agent",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--logo-text", "Apex Bank Credit Policy AI"
    ]

    env = os.environ.copy()
    env["OLLAMA_API_BASE"] = "http://localhost:11434"
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nADK Web Server stopped.")

if __name__ == "__main__":
    main()
