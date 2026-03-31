"""
Jot Forms API integration for SAMA AI.
Handles form creation, submission retrieval, and data analysis.
"""
import os
import requests
from typing import Dict, List, Any
from datetime import datetime

# Load environment variables from .env file if present
_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(_env_path):
    with open(_env_path, 'r', encoding='utf-8') as _env_file:
        for _line in _env_file:
            _line = _line.strip()
            if not _line or _line.startswith('#') or '=' not in _line:
                continue
            _key, _value = _line.split('=', 1)
            os.environ.setdefault(_key.strip(), _value.strip())

# Jot Forms API configuration
JOTFORM_API_KEY = os.environ.get("JOTFORM_API_KEY")
JOTFORM_BASE_URL = "https://api.jotform.com"

class JotFormAgent:
    def __init__(self):
        if not JOTFORM_API_KEY:
            raise ValueError("JOTFORM_API_KEY environment variable not set")
        self.api_key = JOTFORM_API_KEY

    def _get_auth_params(self):
        """Get authentication parameters for API requests."""
        return {"apiKey": self.api_key}

    def _flatten_payload(self, payload: Any, parent_key: str = "") -> Dict[str, str]:
        """Flatten nested form payload into JotForm-style form fields."""
        flat: Dict[str, str] = {}

        def recurse(key: str, value: Any):
            if isinstance(value, dict):
                for child_key, child_value in value.items():
                    next_key = f"{key}[{child_key}]" if key else child_key
                    recurse(next_key, child_value)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    next_key = f"{key}[{index}]"
                    recurse(next_key, item)
            else:
                flat[key] = "" if value is None else str(value)

        recurse(parent_key, payload)
        return flat

    def create_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Jot Form.

        Args:
            form_data: Dictionary containing form properties and questions

        Returns:
            Response from Jot Forms API
        """
        url = f"{JOTFORM_BASE_URL}/form"
        params = self._get_auth_params()
        data = self._flatten_payload(form_data)

        response = requests.post(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def add_question_to_form(self, form_id: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a question to an existing form.

        Args:
            form_id: The form ID
            question_data: Question configuration

        Returns:
            Response from Jot Forms API
        """
        url = f"{JOTFORM_BASE_URL}/form/{form_id}/questions"
        params = self._get_auth_params()
        data = self._flatten_payload({"question": question_data})

        response = requests.post(url, params=params, data=data)
        response.raise_for_status()
        return response.json()

    def get_form_submissions(self, form_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get submissions for a specific form.

        Args:
            form_id: The form ID
            limit: Maximum number of submissions to retrieve

        Returns:
            List of submission data
        """
        url = f"{JOTFORM_BASE_URL}/form/{form_id}/submissions"
        params = self._get_auth_params()
        params["limit"] = limit
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("content", [])

    def analyze_submissions(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze form submissions for insights.

        Args:
            submissions: List of submission dictionaries

        Returns:
            Analysis results with key metrics
        """
        if not submissions:
            return {"total_submissions": 0, "insights": "No submissions to analyze"}

        total_submissions = len(submissions)

        # Basic analysis
        analysis = {
            "total_submissions": total_submissions,
            "date_range": {
                "earliest": min(sub["created_at"] for sub in submissions),
                "latest": max(sub["created_at"] for sub in submissions)
            },
            "insights": []
        }

        # Add more sophisticated analysis based on form fields
        # This would need to be customized per form type

        return analysis

    def get_form_details(self, form_id: str) -> Dict[str, Any]:
        """
        Get details of a specific form.

        Args:
            form_id: The form ID

        Returns:
            Form details
        """
        url = f"{JOTFORM_BASE_URL}/form/{form_id}"
        params = self._get_auth_params()
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("content", {})

    def get_form_questions(self, form_id: str) -> Dict[str, Any]:
        """
        Get the questions for a specific form.

        Args:
            form_id: The form ID

        Returns:
            Dictionary of questions on the form
        """
        url = f"{JOTFORM_BASE_URL}/form/{form_id}/questions"
        params = self._get_auth_params()
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("content", {})

def create_event_registration_form(event_name: str, event_date: str, event_description: str = "") -> Dict[str, Any]:
    """
    Create a standard event registration form.

    Args:
        event_name: Name of the event
        event_date: Date of the event
        event_description: Optional description

    Returns:
        Form creation data for Jot Forms API
    """
    form_data = {
        "properties": {
            "title": f"SAMA Event Registration: {event_name}",
            "height": "600"
        },
        "questions": [
            {
                "type": "control_head",
                "text": f"Register for {event_name}",
                "order": "1",
                "name": "header"
            },
            {
                "type": "control_textbox",
                "text": "Full Name",
                "order": "2",
                "name": "name",
                "validation": "Required"
            },
            {
                "type": "control_email",
                "text": "Email Address",
                "order": "3",
                "name": "email",
                "validation": "Required"
            },
            {
                "type": "control_textbox",
                "text": "Phone Number",
                "order": "4",
                "name": "phone"
            },
            {
                "type": "control_textarea",
                "text": "Special Requirements or Questions",
                "order": "5",
                "name": "notes"
            }
        ]
    }

    if event_description:
        form_data["questions"].insert(1, {
            "type": "control_text",
            "text": event_description,
            "order": "1.5",
            "name": "description"
        })

    return form_data

# Example usage
if __name__ == "__main__":
    agent = JotFormAgent()

    # Example: Create an event registration form
    form_data = create_event_registration_form(
        "Community Mentorship Program",
        "2026-04-15",
        "Join us for our monthly mentorship session focused on personal and professional development."
    )

    try:
        result = agent.create_form(form_data)
        print(f"Form created: {result}")
    except Exception as e:
        print(f"Error creating form: {e}")