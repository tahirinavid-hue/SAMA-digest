"""
Email delivery via Resend API.
"""
import os
import requests

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
SENDER = "onboarding@resend.dev"
RECIPIENTS = [
    "sshafie30@gmail.com",
    "aprilarman33@gmail.com",
    "najeebmian@hotmail.com",
    "semirakhawar@gmail.com",
    "tahirinavid@gmail.com",
]

RESEND_URL = "https://api.resend.com/emails"


def send(subject: str, html: str) -> None:
    resp = requests.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": SENDER,
            "to": RECIPIENTS,
            "subject": subject,
            "html": html,
        },
        timeout=15,
    )
    resp.raise_for_status()
    print(f"[email] Sent: {subject}")
