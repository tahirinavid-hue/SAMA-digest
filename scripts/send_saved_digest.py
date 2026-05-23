"""
Grand Island Community Digest — send the saved digest to all subscribers.
Run this after reviewing the preview email to approve and deliver to everyone.
"""
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.send_gi_email import send

ADMIN_EMAIL = "tahirinavid@gmail.com"
TEST_RECIPIENTS = ["tahirinavid@gmail.com", "faisal_tahiri@hotmail.com"]
ROOT = Path(__file__).parent.parent
LAST_DIGEST_FILE = ROOT / "gi_last_digest.html"


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
            return

    print(f"[send_saved] Sending saved digest to {len(subscribers)} subscriber(s).")
    send(subject, html, subscribers)
    print("[send_saved] Done.")


if __name__ == "__main__":
    main()
