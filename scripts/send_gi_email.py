"""
Email delivery for Grand Island Community Digest via Resend API.
"""
import os
import requests

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
SENDER = "onboarding@resend.dev"
RESEND_URL = "https://api.resend.com/emails"


def send(subject: str, html: str, recipients: list[str]) -> None:
    resp = requests.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": SENDER,
            "to": recipients,
            "subject": subject,
            "html": html,
        },
        timeout=15,
    )
    resp.raise_for_status()
    print(f"[gi_email] Sent to {len(recipients)} recipients: {subject.encode('ascii', errors='replace').decode()}")
