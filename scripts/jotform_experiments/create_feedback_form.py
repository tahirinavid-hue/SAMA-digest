#!/usr/bin/env python3
"""
Create a basic feedback form for SAMA AI community.
This creates an empty form that can be customized through the JotForm web interface.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jot_forms import JotFormAgent

def main():
    agent = JotFormAgent()

    # Create a basic form with proper title and description
    form_data = {
        "properties": {
            "title": "SAMA AI Community Feedback",
            "height": "800",
            "description": "Help us improve SAMA AI by sharing your feedback about our community services, events, and digital tools."
        }
    }

    try:
        result = agent.create_form(form_data)
        print("✅ Feedback form created successfully!")
        print(f"Form ID: {result['content']['id']}")
        print(f"Form URL: {result['content']['url']}")
        print("\n📝 Next steps:")
        print("1. Visit the form URL above")
        print("2. Log in to JotForm")
        print("3. Add the following questions manually:")
        print("   - Name (Text Box)")
        print("   - Email (Email field)")
        print("   - What services have you used? (Checkboxes: Website, Events, Community Digest, Social Media)")
        print("   - How satisfied are you with our services? (Radio Buttons: Very Satisfied, Satisfied, Neutral, Dissatisfied, Very Dissatisfied)")
        print("   - What improvements would you suggest? (Text Area)")
        print("   - Would you like to volunteer or contribute? (Yes/No radio buttons)")
        print("   - Any additional comments? (Text Area)")
        print("4. Save the form")
        print("5. Update the website with the form URL")

        return result['content']['url']

    except Exception as e:
        print(f"❌ Error creating form: {e}")
        return None

if __name__ == "__main__":
    main()