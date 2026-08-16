"""
ProHealth AI Assistant - One-Click Portal Launcher
Runs FastAPI backend and opens web portal in browser
"""

import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    print("\n🌐 Opening ProHealth AI Assistant in your default browser: http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 PROHEALTH AI ASSISTANT - SMART HOSPITAL PORTAL & TRIAGE SYSTEM")
    print("=" * 70)
    print("Starting server on http://localhost:8000 ...")
    
    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Uvicorn server
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=True)
