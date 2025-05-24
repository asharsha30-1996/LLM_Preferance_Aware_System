def parse_feedback(feedback_text):
    if ',' in feedback_text:
        return [item.strip() for item in feedback_text.split(',')]
    return [feedback_text.strip()]
