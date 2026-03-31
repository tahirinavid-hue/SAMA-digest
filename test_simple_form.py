#!/usr/bin/env python3
"""
Simple test script to create a basic JotForm with one question.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jot_forms import JotFormAgent

def main():
    agent = JotFormAgent()

    # Simple form data without questions first
    form_data = {
        "properties": {
            "title": "SAMA Community Feedback Test",
            "height": "600"
        }
    }

    try:
        result = agent.create_form(form_data)
        print("Form created successfully!")
        print(f"Full response: {result}")

        # Check if response has content
        if 'content' in result:
            form_info = result['content']
            form_id = form_info.get('id')
            print(f"Form ID: {form_id}")
            print(f"Form URL: {form_info.get('url')}")

            if form_id:
                # Now add a question - try simpler structure
                question_data = {
                    "qid": "1",
                    "type": "control_textbox",
                    "text": "What is your name?",
                    "name": "name"
                }

                question_result = agent.add_question_to_form(form_id, question_data)
                print(f"Question added: {question_result}")

                # Get form questions to verify creation
                form_questions = agent.get_form_questions(form_id)
                print(f"Number of Questions: {len(form_questions)}")

                # Print question details if any
                if form_questions:
                    for qid, qdata in form_questions.items():
                        print(f"Question {qid}: {qdata.get('text', 'No text')}")
                else:
                    print("No questions found in form questions")
        else:
            print("No 'content' key in response")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()