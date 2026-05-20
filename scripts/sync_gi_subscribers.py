"""
Grand Island Community Digest — subscriber sync.
- Pulls new subscribe/unsubscribe submissions from JotForm
- Updates gi_subscribers.txt
- Sends a polished welcome email to any new subscribers
- Immediately sends the most recent digest to new subscribers if one exists
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jot_forms import JotFormAgent
from scripts.send_gi_email import send

SUBSCRIBE_FORM_ID = "261395184727163"
UNSUBSCRIBE_FORM_ID = "261395766068167"

ROOT = Path(__file__).parent.parent
SUBSCRIBERS_FILE = ROOT / "gi_subscribers.txt"
WELCOMED_FILE = ROOT / "gi_welcomed.txt"

BLUE = "#1a3a5c"
LIGHT_BLUE = "#e8f0f7"
ACCENT = "#2c7be5"


def build_welcome_email(first_name: str = "") -> str:
    name_display = first_name.strip().title() if first_name.strip() else "neighbor"
    return f"""
    <html><body style="background:#f4f6f8;padding:24px;margin:0;">
      <div style="max-width:600px;margin:0 auto;">

        <!-- Hero -->
        <div style="background:{BLUE};border-radius:12px 12px 0 0;padding:48px 40px 40px;text-align:center;">
          <p style="font-family:sans-serif;color:rgba(255,255,255,0.7);font-size:12px;
                    letter-spacing:0.12em;text-transform:uppercase;margin:0 0 12px;">
            Grand Island, NY
          </p>
          <h1 style="font-family:sans-serif;color:#ffffff;font-size:32px;margin:0 0 12px;
                     font-weight:700;line-height:1.2;">
            Welcome to the<br>Community Digest
          </h1>
          <p style="font-family:sans-serif;color:rgba(255,255,255,0.85);font-size:16px;margin:0;">
            Your weekly look at everything happening on the island.
          </p>
        </div>

        <!-- Body -->
        <div style="background:#ffffff;padding:40px;border-left:1px solid #e2e8f0;
                    border-right:1px solid #e2e8f0;">
          <p style="font-family:sans-serif;font-size:16px;color:#2d3748;line-height:1.7;margin:0 0 20px;">
            Hey {name_display}! 👋
          </p>
          <p style="font-family:sans-serif;font-size:15px;color:#4a5568;line-height:1.8;margin:0 0 20px;">
            You're now subscribed to the <strong>Grand Island Community Digest</strong> —
            a free weekly email rounding up the best local events, activities, and things
            to do right here on Grand Island.
          </p>

          <!-- What to expect box -->
          <div style="background:{LIGHT_BLUE};border-radius:8px;padding:24px;margin:28px 0;">
            <p style="font-family:sans-serif;font-size:13px;font-weight:700;color:{BLUE};
                      text-transform:uppercase;letter-spacing:0.08em;margin:0 0 14px;">
              What to expect
            </p>
            <table style="width:100%;border-collapse:collapse;">
              <tr>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#2d3748;
                           vertical-align:top;width:28px;">📅</td>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#4a5568;
                           line-height:1.6;">Upcoming events, festivals &amp; community gatherings</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#2d3748;
                           vertical-align:top;">🙌</td>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#4a5568;
                           line-height:1.6;">Volunteer opportunities &amp; local fundraisers</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#2d3748;
                           vertical-align:top;">👨‍👩‍👧</td>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#4a5568;
                           line-height:1.6;">Family-friendly activities, sports &amp; arts programs</td>
              </tr>
              <tr>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#2d3748;
                           vertical-align:top;">🏛️</td>
                <td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#4a5568;
                           line-height:1.6;">Town meetings, civic news &amp; local updates</td>
              </tr>
            </table>
          </div>

          <p style="font-family:sans-serif;font-size:15px;color:#4a5568;line-height:1.8;margin:0 0 28px;">
            Your first digest will arrive this coming <strong>Saturday morning</strong>.
          </p>

          <p style="font-family:sans-serif;font-size:14px;color:#718096;line-height:1.7;
                    margin:0;border-top:1px solid #e2e8f0;padding-top:20px;">
            Glad to have you. See you Saturday! 🌟
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#f4f6f8;border-radius:0 0 12px 12px;padding:20px 40px;
                    border:1px solid #e2e8f0;border-top:none;text-align:center;">
          <p style="font-family:sans-serif;font-size:11px;color:#a0aec0;margin:0;">
            Grand Island, NY ·
            <a href="https://form.jotform.com/261395766068167"
               style="color:#a0aec0;">Unsubscribe</a>
          </p>
        </div>

      </div>
    </body></html>
    """


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
    SUBSCRIBERS_FILE.write_text("\n".join(lines) + "\n")


def save_welcomed(emails: set[str]) -> None:
    WELCOMED_FILE.write_text("\n".join(sorted(emails)) + "\n")


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
    already_welcomed = load_file_set(WELCOMED_FILE)

    # Collect subscribe submissions
    new_subscribers: dict[str, str] = {}  # email -> first_name
    for sub in get_subscribe_submissions(agent):
        email = extract_field(sub, "email").strip().lower()
        if email:
            new_subscribers[email] = ""

    # Collect unsubscribe submissions
    unsubscribers: set[str] = set()
    for sub in get_unsubscribe_submissions(agent):
        email = extract_field(sub, "email").strip().lower()
        if email:
            unsubscribers.add(email)

    # Build updated subscriber set
    updated = (current_subscribers | set(new_subscribers.keys())) - unsubscribers

    # Send welcome emails to new subscribers who haven't been welcomed yet
    to_welcome = {
        email: name
        for email, name in new_subscribers.items()
        if email not in already_welcomed and email not in unsubscribers
    }

    welcomed_new = set()
    for email, first_name in to_welcome.items():
        try:
            html = build_welcome_email(first_name)
            send("Welcome to the Grand Island Community Digest 🎉", html, [email])
            welcomed_new.add(email)
            print(f"[sync] Welcomed: {email}")
        except Exception as e:
            print(f"[sync] Failed to welcome {email}: {e}")

    # Persist
    save_subscribers(updated)
    save_welcomed(already_welcomed | welcomed_new)

    print(f"[sync] Subscribers: {len(updated)} (+{len(new_subscribers)} new, -{len(unsubscribers)} unsub)")
    print(f"[sync] Welcome emails sent: {len(welcomed_new)}")


if __name__ == "__main__":
    sync()
