import scripts.jot_forms as jf

agent = jf.JotFormAgent()

# Create a proper feedback form using the correct JotForm API format
feedback_form = {
    'properties': {
        'title': 'SAMA Anonymous Feedback Form',
        'height': '600'
    },
    'questions': {
        '1': {
            'type': 'control_head',
            'text': 'SAMA anonymous feedback form',
            'order': '1',
            'name': 'header'
        },
        '2': {
            'type': 'control_textbox',
            'text': 'Name (Optional)',
            'order': '2',
            'name': 'name',
            'required': 'No'
        },
        '3': {
            'type': 'control_email',
            'text': 'Email (Optional - for follow-up only)',
            'order': '3',
            'name': 'email',
            'required': 'No'
        },
        '4': {
            'type': 'control_radio',
            'text': 'How would you rate your overall experience with SAMA?',
            'order': '4',
            'name': 'rating',
            'options': 'Excellent|Good|Average|Poor|Very Poor'
        },
        '5': {
            'type': 'control_textarea',
            'text': 'What did you like most about SAMA?',
            'order': '5',
            'name': 'positive_feedback'
        },
        '6': {
            'type': 'control_textarea',
            'text': 'What can we improve?',
            'order': '6',
            'name': 'improvement_suggestions'
        },
        '7': {
            'type': 'control_checkbox',
            'text': 'Which SAMA programs or services have you participated in? (Select all that apply)',
            'order': '7',
            'name': 'programs_used',
            'options': 'Jumuah Prayer|Weekend Islamic School|Youth Mentorship|Community Events|Other'
        },
        '8': {
            'type': 'control_textarea',
            'text': 'Any other comments or suggestions?',
            'order': '8',
            'name': 'additional_comments'
        }
    }
}

try:
    result = agent.create_form(feedback_form)
    print('New form created successfully!')
    print(f'Form ID: {result["content"]["id"]}')
    print(f'Form URL: {result["content"]["url"]}')
    print(f'Form Title: {result["content"]["title"]}')
except Exception as e:
    print(f'Error creating form: {e}')