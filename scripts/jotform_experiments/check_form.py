import scripts.jot_forms as jf

agent = jf.JotFormAgent()
try:
    form_details = agent.get_form_details('260896470212155')  # New form ID
    print('New form details:')
    print(f'Title: {form_details.get("title", "No title")}')
    print(f'Status: {form_details.get("status", "Unknown")}')
    print(f'Questions: {len(form_details.get("questions", []))}')

    questions = form_details.get('questions', [])
    for i, q in enumerate(questions[:5]):  # Show first 5 questions
        print(f'Question {i+1}: {q.get("text", "No text")} (Type: {q.get("type", "Unknown")})')

except Exception as e:
    print(f'Error getting form details: {e}')