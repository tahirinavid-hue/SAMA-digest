"""
Grand Island Community Digest — subscriber sync.
- Pulls new subscribe/unsubscribe submissions from JotForm
- Updates gi_subscribers.txt
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jot_forms import JotFormAgent

SUBSCRIBE_FORM_ID = "261395184727163"
UNSUBSCRIBE_FORM_ID = "261395766068167"

ROOT = Path(__file__).parent.parent
SUBSCRIBERS_FILE = ROOT / "gi_subscribers.txt"


def load_file_set(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip().lower()
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.startswith("#")
    }


def save_subscribers(emails: set[str]) -> None:
    lines = ["# Grand Island Community Digest — subscriber list",
             "# Managed automatically by sync_gi_subscribers.py",
             "# To manually add/remove, edit this file directly.", ""]
    lines += sorted(emails)
    SUBSCRIBERS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_subscribe_submissions(agent: JotFormAgent) -> list[dict]:
    return agent.get_form_submissions(SUBSCRIBE_FORM_ID, limit=1000)


def get_unsubscribe_submissions(agent: JotFormAgent) -> list[dict]:
    return agent.get_form_submissions(UNSUBSCRIBE_FORM_ID, limit=1000)


def extract_field(submission: dict, name: str) -> str:
    answers = submission.get("answers", {})
    for answer in answers.values():
        if answer.get("name") == name:
            return answer.get("answer", "") or ""
    return ""


def sync() -> None:
    agent = JotFormAgent()

    current_subscribers = load_file_set(SUBSCRIBERS_FILE)

    new_subscribers: set[str] = set()
    for sub in get_subscribe_submissions(agent):
        email = extract_field(sub, "email").strip().lower()
        if email:
            new_subscribers.add(email)

    unsubscribers: set[str] = set()
    for sub in get_unsubscribe_submissions(agent):
        email = extract_field(sub, "email").strip().lower()
        if email:
            unsubscribers.add(email)

    updated = (current_subscribers | new_subscribers) - unsubscribers
    save_subscribers(updated)

    print(f"[sync] Subscribers: {len(updated)} (+{len(new_subscribers - current_subscribers)} new, -{len(unsubscribers)} unsub)")


if __name__ == "__main__":
    sync()
