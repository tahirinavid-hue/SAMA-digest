"""Tests for email delivery module."""
import os
from unittest.mock import patch, MagicMock

# Patch env before importing the module (it reads RESEND_API_KEY at import time)
with patch.dict(os.environ, {"RESEND_API_KEY": "test_key_123"}):
    import scripts.send_email as send_email


def test_send_calls_resend_api():
    """send() should POST to the Resend API with correct payload."""
    with patch("scripts.send_email.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_email.send("Test Subject", "<p>Hello</p>")

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]

        assert payload["subject"] == "Test Subject"
        assert payload["html"] == "<p>Hello</p>"
        assert len(payload["to"]) == 5  # all board members


def test_send_includes_all_recipients():
    """All 5 SAMA board members should be in the recipient list."""
    assert len(send_email.RECIPIENTS) == 5
