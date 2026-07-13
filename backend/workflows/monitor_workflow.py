"""Render Background Worker — durable 3-step monitoring workflow."""
import time
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def step1_fetch_signals() -> int:
    """Step 1: Fetch current signal count from backend."""
    try:
        response = httpx.get(f"{BACKEND_URL}/signals?limit=50", timeout=10)
        data = response.json()
        count = data.get("total", 0)
        print(f"  [Step 1] Fetched {count} signals from backend")
        return count
    except Exception as e:
        print(f"  [Step 1] Failed to fetch signals: {e}")
        return 0


def step2_check_thresholds() -> list:
    """Step 2: Identify signals exceeding critical threshold (LSI >= 75)."""
    try:
        response = httpx.get(f"{BACKEND_URL}/signals?limit=50", timeout=10)
        data = response.json()
        signals = data.get("signals", [])
        critical = [
            s["signal_id"] for s in signals
            if s.get("lsi_score", 0) >= 75
        ]
        print(f"  [Step 2] Found {len(critical)} critical signals")
        return critical
    except Exception as e:
        print(f"  [Step 2] Threshold check failed: {e}")
        return []


def step3_log_escalations(critical_signals: list) -> None:
    """Step 3: Log escalations for critical signals."""
    try:
        if critical_signals:
            print(f"  [Step 3] ESCALATION REQUIRED — {len(critical_signals)} critical signal(s):")
            for signal_id in critical_signals:
                print(f"    → {signal_id}")
        else:
            print(f"  [Step 3] No escalations required")
    except Exception as e:
        print(f"  [Step 3] Escalation logging failed: {e}")


def run_monitoring_cycle() -> None:
    """Run one full monitoring cycle with independent step error handling."""
    print(f"\n[{datetime.now().isoformat()}] Starting monitoring cycle")

    try:
        count = step1_fetch_signals()
    except Exception as e:
        print(f"  Step 1 failed: {e}. Continuing to step 2.")
        count = 0

    try:
        critical = step2_check_thresholds()
    except Exception as e:
        print(f"  Step 2 failed: {e}. Continuing to step 3.")
        critical = []

    try:
        step3_log_escalations(critical)
    except Exception as e:
        print(f"  Step 3 failed: {e}")

    print(f"  Cycle complete. Sleeping 30 minutes.")


if __name__ == "__main__":
    print("[Astra Monitor] Starting durable monitoring workflow")
    while True:
        run_monitoring_cycle()
        time.sleep(1800)