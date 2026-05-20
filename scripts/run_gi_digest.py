"""
Grand Island Community Digest — main entry point.
Runs every Monday. Sends HTML email via Resend to all GI subscribers.
Saves the latest digest HTML to gi_last_digest.html for new-subscriber delivery.
"""
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import markdown as md

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import gi_community_digest
from scripts.send_gi_email import send

BLUE = "#1a3a5c"
LIGHT = "#e8f0f7"
ACCENT = "#2c7be5"
ADMIN_EMAIL = "tahirinavid@gmail.com"

ROOT = Path(__file__).parent.parent
LAST_DIGEST_FILE = ROOT / "gi_last_digest.html"

FEEDBACK_URL = "https://form.jotform.com/261395270591158"
SUBSCRIBE_URL = "https://form.jotform.com/261395184727163"
UNSUBSCRIBE_URL = "https://form.jotform.com/261395766068167"


def build_html(digest: str, date_str: str) -> str:
    return f"""
    <html><body style="background:#eef2f7;padding:24px;margin:0;">
      <div style="max-width:660px;margin:0 auto;">

        <!-- Header bar -->
        <div style="background:{BLUE};border-radius:10px 10px 0 0;padding:28px 32px 24px;">
          <div style="font-family:sans-serif;font-size:11px;font-weight:600;color:rgba(255,255,255,0.55);
                      letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;">
            Grand Island, NY
          </div>
          <div style="font-family:sans-serif;font-size:22px;font-weight:700;color:#ffffff;
                      line-height:1.2;">
            🏝️ Community Events Digest
          </div>
          <div style="font-family:sans-serif;font-size:12px;color:rgba(255,255,255,0.6);
                      margin-top:6px;">{date_str}</div>
        </div>

        <!-- Body -->
        <div style="background:#ffffff;border-radius:0 0 10px 10px;padding:32px;
                    border:1px solid #dde3ed;border-top:none;">
        <style>
          h1 {{ font-family:sans-serif; font-size:20px; font-weight:700; color:{BLUE}; margin:0 0 4px; }}
          em {{ font-family:sans-serif; font-size:13px; color:#718096; font-style:italic; display:block; margin-bottom:20px; }}
          h2 {{ font-family:sans-serif; font-size:13px; font-weight:700; color:{ACCENT};
                text-transform:uppercase; letter-spacing:0.1em; margin:28px 0 12px;
                padding-bottom:6px; border-bottom:2px solid {LIGHT}; }}
          h3 {{ font-family:sans-serif; font-size:17px; font-weight:700; color:{BLUE};
                margin:0 0 14px; letter-spacing:0.01em; }}
          p  {{ font-family:sans-serif; font-size:14px; color:#4a5568; line-height:1.8; margin:4px 0 12px; }}
          strong {{ color:#1a202c; }}
          ol  {{ padding-left:20px; margin:0 0 20px; }}
          ol li {{ font-family:sans-serif; font-size:14px; color:#2d3748; line-height:1.9; padding:2px 0; }}
          hr  {{ border:none; border-top:1px solid #e2e8f0; margin:24px 0; }}
        </style>
        <div style="font-family:sans-serif;font-size:14px;color:#2d3748;line-height:1.8;">
          {digest}
        </div>
        <div style="background:{LIGHT};border-radius:8px;padding:20px 24px;margin-top:32px;">
          <p style="font-family:sans-serif;font-size:13px;font-weight:700;color:{BLUE};
                    text-transform:uppercase;letter-spacing:0.08em;margin:0 0 6px;">
            Send Feedback
          </p>
          <p style="font-family:sans-serif;font-size:13px;color:#4a5568;margin:0 0 14px;
                    line-height:1.6;">
            Know about an event we missed? Have a suggestion? We'd love to hear from you.
          </p>
          <a href="{FEEDBACK_URL}"
             style="display:inline-block;background:{BLUE};color:#ffffff;
                    font-family:sans-serif;font-size:13px;font-weight:600;
                    text-decoration:none;padding:10px 22px;border-radius:5px;">
            Share Your Feedback →
          </a>
        </div>
        <p style="font-family:sans-serif;font-size:11px;color:#a0aec0;margin-top:24px;
                  text-align:center;border-top:1px solid #e2e8f0;padding-top:16px;">
          This is an independent community newsletter and is not affiliated with or
          endorsed by the Town of Grand Island or any official government body. ·
          Grand Island, NY ·
          <a href="{UNSUBSCRIBE_URL}" style="color:#a0aec0;">Unsubscribe</a>
        </p>
        </div><!-- /body -->
      </div><!-- /outer -->
    </body></html>
    """


DIGEST_HEADER = "# Grand Island, NY"


def clean_digest(raw: str) -> str:
    """Strip AI preamble before the digest header and remove any date range line after it."""
    lines = raw.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(DIGEST_HEADER):
            start = i
            break
    if start is None:
        raise ValueError(
            "Digest header '# 🏝️' not found in generated output. "
            "Refusing to send — output may be malformed."
        )
    print(f"[run_gi_digest] Digest starts at line {start + 1} — preamble stripped.")
    kept = [lines[start]]  # the # 🏝️ header line
    # Skip any immediately following date-range line (e.g. "May 24 – June 7, 2026")
    rest = lines[start + 1:]
    for j, line in enumerate(rest):
        stripped = line.strip()
        # A date-range line matches "Month DD" at the start — skip it
        import re
        if re.match(r'^[A-Z][a-z]+ \d', stripped) and ('–' in stripped or '-' in stripped or ',' in stripped):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def validate_event_numbers(digest_md: str) -> str:
    """Check summary/detail event numbers align. Auto-corrects mismatches by rebuilding summary."""
    # Summary lines: "1. **Event Name** · Date"
    summary_nums = re.findall(r'^(\d+)\.\s+\*\*', digest_md, re.MULTILINE)
    # Detail lines: "**1. emoji Event Name**"
    detail_nums = re.findall(r'^\*\*(\d+)\.\s+', digest_md, re.MULTILINE)

    if not detail_nums:
        raise ValueError("Validation failed: no numbered events found in detail section.")

    if not summary_nums:
        raise ValueError("Validation failed: no numbered events found in summary section.")

    if len(summary_nums) == len(detail_nums):
        print(f"[run_gi_digest] Validation passed — {len(summary_nums)} events, numbers aligned.")
        return digest_md

    # Mismatch — rebuild the summary from detail event names
    print(f"[run_gi_digest] Summary/detail mismatch ({len(summary_nums)} vs {len(detail_nums)}) — rebuilding summary.")

    # Extract detail event lines: "**N. emoji Name**\nDate, time, location"
    detail_blocks = re.findall(r'^\*\*\d+\.\s+.+?\*\*\n(.+?)$', digest_md, re.MULTILINE)
    detail_headers = re.findall(r'^\*\*(\d+)\.\s+(?:.+?\s+)?(.+?)\*\*', digest_md, re.MULTILINE)

    new_summary_lines = []
    for num, name in detail_headers:
        # Find the date line immediately after this header
        pattern = rf'^\*\*{num}\..+?\*\*\n(.+?)$'
        match = re.search(pattern, digest_md, re.MULTILINE)
        date_str = match.group(1).split(",")[0].strip() if match else ""
        new_summary_lines.append(f"{num}. **{name.strip()}** · {date_str}")

    new_summary = "\n".join(new_summary_lines)

    # Replace old summary block (between ### Upcoming Events and ---)
    digest_md = re.sub(
        r'(### Upcoming Events\n)(.*?)(\n---)',
        rf'\g<1>{new_summary}\g<3>',
        digest_md,
        flags=re.DOTALL
    )
    print(f"[run_gi_digest] Summary rebuilt with {len(detail_headers)} events.")
    return digest_md


def load_subscribers() -> list[str]:
    subs_path = ROOT / "gi_subscribers.txt"
    if not subs_path.exists():
        return []
    lines = subs_path.read_text().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def main():
    now = datetime.now(timezone.utc)
    is_saturday = now.weekday() == 5
    force_send = os.environ.get("FORCE_SEND", "").lower() == "true"
    test_mode = os.environ.get("TEST_MODE", "").lower() == "true"

    if not is_saturday and not force_send:
        print("[run_gi_digest] Not Saturday — nothing to send.")
        return

    if test_mode:
        subscribers = [ADMIN_EMAIL]
        print(f"[run_gi_digest] TEST MODE — sending only to {ADMIN_EMAIL}")
    else:
        subscribers = load_subscribers()
        if not subscribers:
            print("[run_gi_digest] No subscribers — nothing to send.")
            return

    date_str = now.strftime("%B %-d, %Y")
    subject = f"Grand Island Community Digest — {date_str}"

    print(f"[run_gi_digest] Monday {date_str} — running digest for {len(subscribers)} subscribers")

    digest_md = gi_community_digest.generate()
    digest_md = clean_digest(digest_md)
    digest_md = validate_event_numbers(digest_md)

    digest_html = md.markdown(digest_md, extensions=["extra"])

    html = build_html(digest_html, date_str)

    # Save for new-subscriber immediate delivery
    LAST_DIGEST_FILE.write_text(html, encoding="utf-8")
    print(f"[run_gi_digest] Saved last digest to {LAST_DIGEST_FILE.name}")

    send(subject, html, subscribers)
    print("[run_gi_digest] Done.")


if __name__ == "__main__":
    main()
