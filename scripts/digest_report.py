"""
Grand Island Community Digest — post-send analyst report.
Reads delivery stats and subscriber data, emails a summary to the admin.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.send_gi_email import send

ADMIN_EMAIL = "tahirinavid@gmail.com"
ROOT = Path(__file__).parent.parent
STATS_FILE = ROOT / "gi_send_stats.json"
STATE_FILE = ROOT / "gi_digest_state.json"  # persisted week-over-week
SUBSCRIBERS_FILE = ROOT / "gi_subscribers.txt"
WELCOMED_FILE = ROOT / "gi_welcomed.txt"

BLUE = "#1a3a5c"
LIGHT = "#e8f0f7"
ACCENT = "#2c7be5"
GREEN = "#38a169"
RED = "#e53e3e"


def load_subscribers() -> list[str]:
    if not SUBSCRIBERS_FILE.exists():
        return []
    return [
        line.strip()
        for line in SUBSCRIBERS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def load_welcomed() -> list[str]:
    if not WELCOMED_FILE.exists():
        return []
    return [
        line.strip()
        for line in WELCOMED_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip()
    ]


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"total_subscribers": 0, "welcomed": [], "last_send_date": "N/A"}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def pct(n, total) -> str:
    if total == 0:
        return "—"
    return f"{n / total * 100:.0f}%"


def stat_box(label: str, value: str, color: str = BLUE, sub: str = "") -> str:
    sub_html = f'<div style="font-size:11px;color:#718096;margin-top:2px;">{sub}</div>' if sub else ""
    return f"""
    <td style="padding:12px;text-align:center;background:#ffffff;border-radius:8px;
               border:1px solid #e2e8f0;min-width:100px;">
      <div style="font-family:sans-serif;font-size:28px;font-weight:700;color:{color};">{value}</div>
      <div style="font-family:sans-serif;font-size:11px;font-weight:600;color:#718096;
                  text-transform:uppercase;letter-spacing:0.08em;margin-top:4px;">{label}</div>
      {sub_html}
    </td>"""


def email_row(email: str, badge_color: str, badge_text: str) -> str:
    return f"""
    <tr>
      <td style="font-family:monospace;font-size:13px;color:#2d3748;padding:8px 12px;
                 border-bottom:1px solid #f0f0f0;">{email}</td>
      <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:right;">
        <span style="background:{badge_color};color:#fff;font-family:sans-serif;font-size:10px;
                     font-weight:600;padding:2px 8px;border-radius:10px;">{badge_text}</span>
      </td>
    </tr>"""


def build_report(stats: dict, subscribers: list[str], welcomed: list[str], prev_state: dict) -> str:
    date_str = stats.get("date", "Unknown")
    sent = stats.get("sent", 0)
    failed = stats.get("failed", [])
    total = stats.get("total", 0)
    test_mode = stats.get("test_mode", False)

    prev_total = prev_state.get("total_subscribers", 0)
    prev_welcomed = set(prev_state.get("welcomed", []))
    current_welcomed = set(welcomed)

    new_subs = [e for e in current_welcomed if e not in prev_welcomed]
    net_change = len(subscribers) - prev_total
    net_label = f"+{net_change}" if net_change >= 0 else str(net_change)
    net_color = GREEN if net_change >= 0 else RED

    test_banner = f"""
    <div style="background:#fef3c7;border:1px solid #f6ad55;border-radius:6px;
                padding:10px 16px;margin-bottom:20px;font-family:sans-serif;
                font-size:12px;color:#92400e;">
      <strong>TEST MODE</strong> — digest was sent to test recipients only, not the full subscriber list.
    </div>""" if test_mode else ""

    new_subs_rows = "".join(email_row(e, GREEN, "NEW") for e in sorted(new_subs)) or \
        '<tr><td colspan="2" style="font-family:sans-serif;font-size:13px;color:#a0aec0;padding:8px 12px;">No new subscribers this week.</td></tr>'

    failed_rows = "".join(email_row(e, RED, "FAILED") for e in sorted(failed)) or \
        '<tr><td colspan="2" style="font-family:sans-serif;font-size:13px;color:#a0aec0;padding:8px 12px;">No failures.</td></tr>'

    now_str = datetime.now(ZoneInfo("America/New_York")).strftime("%B %d, %Y at %I:%M %p ET")

    return f"""
    <html><body style="background:#eef2f7;padding:24px;margin:0;">
      <div style="max-width:660px;margin:0 auto;">

        <!-- Header -->
        <div style="background:{BLUE};border-radius:10px 10px 0 0;padding:28px 32px 24px;">
          <div style="font-family:sans-serif;font-size:11px;font-weight:600;
                      color:rgba(255,255,255,0.55);letter-spacing:0.12em;
                      text-transform:uppercase;margin-bottom:6px;">Grand Island Digest</div>
          <div style="font-family:sans-serif;font-size:22px;font-weight:700;color:#ffffff;">
            📊 Send Report
          </div>
          <div style="font-family:sans-serif;font-size:12px;color:rgba(255,255,255,0.6);margin-top:6px;">
            {date_str} · Generated {now_str}
          </div>
        </div>

        <!-- Body -->
        <div style="background:#ffffff;border-radius:0 0 10px 10px;padding:32px;
                    border:1px solid #dde3ed;border-top:none;">

          {test_banner}

          <!-- Top-line stats -->
          <p style="font-family:sans-serif;font-size:12px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 12px;">
            Delivery Summary
          </p>
          <table style="width:100%;border-collapse:separate;border-spacing:8px;margin-bottom:28px;">
            <tr>
              {stat_box("Sent", str(sent), GREEN)}
              {stat_box("Failed", str(len(failed)), RED if failed else "#a0aec0")}
              {stat_box("Success Rate", pct(sent, total), ACCENT)}
              {stat_box("Total List", str(len(subscribers)), BLUE, f"{net_label} vs last week")}
            </tr>
          </table>

          <!-- Subscriber growth -->
          <p style="font-family:sans-serif;font-size:12px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 12px;">
            Subscriber Activity
          </p>
          <table style="width:100%;border-collapse:separate;border-spacing:8px;margin-bottom:28px;">
            <tr>
              {stat_box("New This Week", str(len(new_subs)), GREEN)}
              {stat_box("Total Subscribers", str(len(subscribers)), BLUE)}
              {stat_box("Last Week", str(prev_total), "#718096")}
              {stat_box("Net Change", net_label, net_color)}
            </tr>
          </table>

          <!-- New subscribers detail -->
          <p style="font-family:sans-serif;font-size:12px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 8px;">
            New Subscribers
          </p>
          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;
                        border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;">
            {new_subs_rows}
          </table>

          <!-- Failures detail -->
          <p style="font-family:sans-serif;font-size:12px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 8px;">
            Delivery Failures
          </p>
          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;
                        border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;">
            {failed_rows}
          </table>

          <!-- Full subscriber list -->
          <p style="font-family:sans-serif;font-size:12px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.1em;margin:0 0 8px;">
            Full Subscriber List ({len(subscribers)})
          </p>
          <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;
                        border-radius:6px;overflow:hidden;margin-bottom:8px;">
            {"".join(email_row(e, ACCENT, "ACTIVE") for e in sorted(subscribers))}
          </table>

        </div>
      </div>
    </body></html>
    """


def main():
    if not STATS_FILE.exists():
        print("[digest_report] No stats file found — skipping report.")
        return

    stats = json.loads(STATS_FILE.read_text(encoding="utf-8"))
    subscribers = load_subscribers()
    welcomed = load_welcomed()
    prev_state = load_state()

    html = build_report(stats, subscribers, welcomed, prev_state)

    date_str = stats.get("date", "Unknown")
    subject = f"📊 Digest Send Report — {date_str}"
    send(subject, html, [ADMIN_EMAIL])
    print(f"[digest_report] Report sent to {ADMIN_EMAIL}")

    # Update persisted state for next week's comparison
    save_state({
        "total_subscribers": len(subscribers),
        "welcomed": welcomed,
        "last_send_date": date_str,
    })
    print("[digest_report] State updated for next week.")


if __name__ == "__main__":
    main()
