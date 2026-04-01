"""Tests for JotForm agent module."""
import pytest
from unittest.mock import patch
from scripts.jot_forms import JotFormAgent


def test_jotform_agent_requires_api_key():
    """JotFormAgent should raise if JOTFORM_API_KEY is missing."""
    with patch("scripts.jot_forms.JOTFORM_API_KEY", None):
        with pytest.raises(ValueError, match="JOTFORM_API_KEY"):
            JotFormAgent()


def test_jotform_agent_initializes_with_key():
    """JotFormAgent should store the API key when present."""
    with patch("scripts.jot_forms.JOTFORM_API_KEY", "test_key"):
        agent = JotFormAgent()
        assert agent.api_key == "test_key"
