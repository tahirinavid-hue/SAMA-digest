"""
Grand Island Community Digest — send the saved digest to all subscribers.
Run this after reviewing the preview email to approve and deliver to everyone.
Returns delivery stats written to gi_send_stats.json for the report step.
"""
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.send_gi_email import send

ADMIN_EMAIL = "tahirinavid@gmail.com"
TEST_RECIPIENTS = ["tahirinavid@gmail.com", "faisal_tahiri@hotmail.com"]
ROOT = Path(__file__).parent.parent
LAST_DIGEST_FILE = ROOT / "gi_last_digest.html"
STATS_FILE = ROOT / "gi_send_stats.json"


def load_subscribers() -> list[str]:
    subs_path = ROOT / "gi_subscribers.txt"
    if not subs_path.exists():
        return []
    return [
        line.strip()
        for line in subs_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def main():
    if not LAST_DIGEST_FILE.exists():
        print("[send_saved] No saved digest found — run the generate step first.")
        sys.exit(1)

    html = LAST_DIGEST_FILE.read_text(encoding="utf-8")

    test_mode = os.environ.get("TEST_MODE", "").lower() == "true"

    now = datetime.now(ZoneInfo("America/New_York"))
    date_str = now.strftime("%B %d, %Y").replace(" 0", " ")
    subject = f"Grand Island Community Digest — {date_str}"

    if test_mode:
        subscribers = TEST_RECIPIENTS
        print(f"[send_saved] TEST MODE — sending to {', '.join(TEST_RECIPIENTS)}")
    else:
        subscribers = load_subscribers()
        if not subscribers:
            print("[send_saved] No subscribers — nothing to send.")
            STATS_FILE.write_text(json.dumps({"sent": 0, "failed": [], "total": 0, "date": date_str, "test_mode": False}))
            return

    # Send individually and track results
    failed = []
    succeeded = 0
    import requests
    from scripts.send_gi_email import RESEND_API_KEY, SENDER, RESEND_URL

    for email in subscribers:
        resp = requests.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={"from": SENDER, "to": [email], "subject": subject, "html": html},
            timeout=15,
        )
        if resp.ok:
            succeeded += 1
        else:
            failed.append(email)
            print(f"[send_saved] Failed to send to {email}: {resp.status_code} {resp.text}")

    print(f"[send_saved] Sent {succeeded}/{len(subscribers)}, {len(failed)} failed.")

    stats = {
        "date": date_str,
        "sent": succeeded,
        "failed": failed,
        "total": len(subscribers),
        "test_mode": test_mode,
    }
    STATS_FILE.write_text(json.dumps(stats, indent=2))
    print(f"[send_saved] Stats written to {STATS_FILE.name}")


if __name__ == "__main__":
    main()
