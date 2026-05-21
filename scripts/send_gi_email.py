"""
Email delivery for Grand Island Community Digest via Resend API.
"""
import os
import requests

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
SENDER = "Grand Island Digest <hello@grandislanddigest.com>"
RESEND_URL = "https://api.resend.com/emails"


def send(subject: str, html: str, recipients: list[str]) -> None:
    failed = 0
    for email in recipients:
        resp = requests.post(
            RESEND_URL,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": SENDER,
                "to": [email],
                "subject": subject,
                "html": html,
            },
            timeout=15,
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            print(f"[gi_email] Failed to send to {email}: {e}")
            failed += 1
    sent = len(recipients) - failed
    print(f"[gi_email] Sent to {sent}/{len(recipients)} recipients: {subject.encode('ascii', errors='replace').decode()}")
