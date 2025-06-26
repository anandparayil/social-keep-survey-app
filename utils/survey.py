"""
Survey utilities for Social Keep
"""
from datetime import datetime, timedelta
import json

def calculate_survey_end_time(start_time, survey_type):
    """Calculate when a survey should end based on type"""
    if survey_type == 'daily':
        return start_time + timedelta(hours=24)
    elif survey_type == 'biweekly':
        return start_time + timedelta(weeks=1)
    else:
        raise ValueError(f"Unknown survey type: {survey_type}")

def is_survey_active(survey):
    """Check if a survey is currently active"""
    now = datetime.now()
    return (survey['status'] == 'current' and 
            survey['start_time'] <= now <= survey['end_time'])

def is_survey_expired(survey):
    """Check if a survey has expired"""
    now = datetime.now()
    return now > survey['end_time']

def format_survey_duration(survey_type):
    """Get human-readable duration for survey type"""
    if survey_type == 'daily':
        return '24 hours'
    elif survey_type == 'biweekly':
        return '1 week'
    else:
        return 'Unknown duration'

def validate_survey_data(survey_data):
    """Validate survey creation data"""
    errors = []
    
    if not survey_data.get('survey_name', '').strip():
        errors.append('Survey name is required')
    
    if survey_data.get('survey_type') not in ['daily', 'biweekly']:
        errors.append('Valid survey type is required')
    
    if not survey_data.get('questions'):
        errors.append('At least one question is required')
    
    # Validate questions
    for i, question in enumerate(survey_data.get('questions', [])):
        if not question.get('text', '').strip():
            errors.append(f'Question {i+1} text is required')
        
        if question.get('type') not in ['radio', 'checkbox', 'text']:
            errors.append(f'Question {i+1} has invalid type')
        
        if question.get('type') in ['radio', 'checkbox']:
            options = question.get('options', [])
            if len(options) < 2:
                errors.append(f'Question {i+1} needs at least 2 options')
    
    return errors

def process_survey_responses(responses):
    """Process and validate survey responses"""
    processed = {}
    
    for question_id, response in responses.items():
        if isinstance(response, list):
            # Multiple choice responses
            processed[question_id] = {
                'type': 'multiple',
                'values': response,
                'text': ', '.join(response)
            }
        else:
            # Single response
            processed[question_id] = {
                'type': 'single',
                'value': response,
                'text': str(response)
            }
    
    return processed

def get_survey_statistics(survey_id, connection):
    """Get statistics for a specific survey"""
    with connection.cursor() as cursor:
        # Get total completions
        cursor.execute("""
            SELECT COUNT(*) as total_completions
            FROM survey_completions 
            WHERE survey_id = %s
        """, (survey_id,))
        completions = cursor.fetchone()['total_completions']
        
        # Get total participants
        cursor.execute("""
            SELECT COUNT(*) as total_participants
            FROM users 
            WHERE user_type = 'participant' AND is_activated = TRUE
        """, ())
        participants = cursor.fetchone()['total_participants']
        
        # Calculate completion rate
        completion_rate = (completions / participants * 100) if participants > 0 else 0
        
        return {
            'total_completions': completions,
            'total_participants': participants,
            'completion_rate': round(completion_rate, 2)
        }