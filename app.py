from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
from functools import wraps
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from utils.email import send_credentials_email  
import secrets

app = Flask(__name__)
app.config.from_object(Config)

# Initialize scheduler for automatic survey status updates
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def update_survey_status():
    """Update survey status based on current time"""
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                now = datetime.now()
                
                # Move upcoming surveys to current if start time has passed
                cursor.execute("""
                    UPDATE surveys 
                    SET status = 'current' 
                    WHERE status = 'upcoming' AND start_time <= %s
                """, (now,))
                
                # Move current surveys to closed if end time has passed
                cursor.execute("""
                    UPDATE surveys 
                    SET status = 'closed' 
                    WHERE status = 'current' AND end_time <= %s
                """, (now,))
                
                connection.commit()
        finally:
            connection.close()
    except Exception as e:
        print(f"Error updating survey status: {e}")

# Schedule survey status updates every minute
scheduler.add_job(func=update_survey_status, trigger="interval", minutes=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = 'admin'
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
                if cursor.fetchone():
                    flash('User with this email or username already exists!', 'error')
                    return render_template('auth/register.html')
                
                # Create new user
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, user_type, is_activated) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, email, password_hash, user_type, True))
                connection.commit()
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        finally:
            connection.close()
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_type'] = user['user_type']
                    session['email'] = user['email']
                    
                    flash(f'Welcome back, {user["username"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password!', 'error')
        finally:
            connection.close()
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session['user_type'] == 'admin':
        return render_template('admin/dashboard.html')
    else:
        return render_template('participant/dashboard.html')

# Admin Routes
@app.route('/admin/create_survey')
@login_required
@admin_required
def create_survey():
    return render_template('admin/create_survey.html')

@app.route('/admin/register_participant', methods=['POST', 'GET'])
@login_required
@admin_required
def register_participant():
    if request.method == 'GET':
        return render_template('admin/register_participant.html')
    
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return jsonify({'success': False, 'message': 'Name and email are required.'})

        password = secrets.token_urlsafe(8)  # Auto-generate password
        password_hash = generate_password_hash(password)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'User with this email already exists.'})

                # Insert new participant
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, user_type, is_activated)
                    VALUES (%s, %s, %s, 'participant', TRUE)
                """, (name, email, password_hash))
                connection.commit()

            # Send credentials via email
            if send_credentials_email(email, name, password):
                return jsonify({'success': True, 'message': 'Participant registered and email sent.'})
            else:
                return jsonify({'success': True, 'message': 'Registered, but failed to send email.'})

        finally:
            connection.close()

    except Exception as e:
        print(f"Error in register_participant: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'})

@app.route('/admin/submit_survey', methods=['POST'])
@login_required
@admin_required
def admin_submit_survey():  # Renamed function to avoid conflict
    data = request.get_json()
    
    survey_name = data['survey_name']
    survey_type = data['survey_type']
    questions = data['questions']
    reward_tokens = data.get('reward_tokens', 0)
    start_time = data.get('start_time')
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Calculate end time based on survey type
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                status = 'upcoming'
            else:
                start_dt = datetime.now()
                status = 'current'
            
            if survey_type == 'daily':
                end_dt = start_dt + timedelta(hours=24)
            else:  # biweekly
                end_dt = start_dt + timedelta(weeks=1)
            
            # Insert survey
            cursor.execute("""
                INSERT INTO surveys (name, survey_type, status, start_time, end_time, reward_tokens, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (survey_name, survey_type, status, start_dt, end_dt, reward_tokens, session['user_id']))
            
            survey_id = cursor.lastrowid
            
            # Insert questions and options
            for i, question in enumerate(questions):
                cursor.execute("""
                    INSERT INTO survey_questions (survey_id, question_text, question_type, question_order)
                    VALUES (%s, %s, %s, %s)
                """, (survey_id, question['text'], question['type'], i + 1))
                
                question_id = cursor.lastrowid
                
                # Insert options for radio and checkbox questions
                if question['type'] in ['radio', 'checkbox'] and 'options' in question:
                    for j, option in enumerate(question['options']):
                        cursor.execute("""
                            INSERT INTO survey_options (question_id, option_text, option_order)
                            VALUES (%s, %s, %s)
                        """, (question_id, option, j + 1))
            
            connection.commit()
            return jsonify({'success': True, 'message': f'{survey_type.title()} survey created successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        connection.close()

@app.route('/admin/track_activation')
@login_required
@admin_required
def track_activation():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT username, email, is_activated, created_at 
                FROM users 
                WHERE user_type = 'participant'
                ORDER BY created_at DESC
            """)
            participants = cursor.fetchall()
            return render_template('admin/track_activation.html', participants=participants)
    finally:
        connection.close()

@app.route('/admin/survey_completion')
@login_required
@admin_required
def survey_completion():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.name as survey_name, u.username, sc.completed_at, sc.tokens_earned
                FROM survey_completions sc
                JOIN surveys s ON sc.survey_id = s.id
                JOIN users u ON sc.participant_id = u.id
                ORDER BY sc.completed_at DESC
            """)
            completions = cursor.fetchall()
            return render_template('admin/survey_completion.html', completions=completions)
    finally:
        connection.close()

@app.route('/admin/pending_surveys')
@login_required
@admin_required
def pending_surveys():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.username, s.name as survey_name, s.survey_type, s.end_time
                FROM users u
                CROSS JOIN surveys s
                LEFT JOIN survey_completions sc ON u.id = sc.participant_id AND s.id = sc.survey_id
                WHERE u.user_type = 'participant' 
                AND s.status = 'current' 
                AND sc.id IS NULL
                ORDER BY s.end_time ASC
            """)
            pending = cursor.fetchall()
            return render_template('admin/pending_surveys.html', pending=pending)
    finally:
        connection.close()

@app.route('/admin/error_detection')
@login_required
@admin_required
def error_detection():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.name, s.survey_type, s.end_time,
                       COUNT(sc.id) as completion_count
                FROM surveys s
                LEFT JOIN survey_completions sc ON s.id = sc.survey_id
                WHERE s.status = 'closed' AND s.end_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY s.id
                HAVING completion_count = 0
                ORDER BY s.end_time DESC
            """)
            errors = cursor.fetchall()
            return render_template('admin/error_detection.html', errors=errors)
    finally:
        connection.close()

@app.route('/admin/survey_schedule', methods=['GET', 'POST'])
@login_required
@admin_required
def survey_schedule():
    if request.method == 'POST':
        survey_name = request.form['survey_name']
        survey_type = request.form['survey_type']
        scheduled_date = request.form['scheduled_date']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO survey_schedule (survey_name, survey_type, scheduled_date, created_by)
                    VALUES (%s, %s, %s, %s)
                """, (survey_name, survey_type, scheduled_date, session['user_id']))
                connection.commit()
                flash('Survey scheduled successfully!', 'success')
        finally:
            connection.close()
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM survey_schedule 
                WHERE scheduled_date > NOW()
                ORDER BY scheduled_date ASC
            """)
            schedules = cursor.fetchall()
            return render_template('admin/survey_schedule.html', schedules=schedules)
    finally:
        connection.close()

# Participant Routes
@app.route('/participant/available_surveys')
@login_required
def available_surveys():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, 
                       CASE WHEN sc.id IS NOT NULL THEN 1 ELSE 0 END as completed
                FROM surveys s
                LEFT JOIN survey_completions sc ON s.id = sc.survey_id AND sc.participant_id = %s
                WHERE s.status = 'current'
                ORDER BY s.end_time ASC
            """, (session['user_id'],))
            surveys = cursor.fetchall()
            return render_template('participant/available_surveys.html', surveys=surveys)
    finally:
        connection.close()

@app.route('/participant/upcoming_surveys')
@login_required
def upcoming_surveys():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM surveys 
                WHERE status = 'upcoming'
                ORDER BY start_time ASC
            """)
            surveys = cursor.fetchall()
            return render_template('participant/upcoming_surveys.html', surveys=surveys)
    finally:
        connection.close()

@app.route('/participant/survey_schedule')
@login_required
def participant_survey_schedule():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM survey_schedule 
                WHERE scheduled_date > NOW()
                ORDER BY scheduled_date ASC
            """)
            schedules = cursor.fetchall()
            return render_template('participant/survey_schedule.html', schedules=schedules)
    finally:
        connection.close()

@app.route('/participant/take_survey/<int:survey_id>')
@login_required
def take_survey(survey_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if already completed
            cursor.execute("""
                SELECT id FROM survey_completions 
                WHERE survey_id = %s AND participant_id = %s
            """, (survey_id, session['user_id']))
            
            if cursor.fetchone():
                flash('You have already completed this survey!', 'info')
                return redirect(url_for('available_surveys'))
            
            # Get survey details
            cursor.execute("SELECT * FROM surveys WHERE id = %s AND status = 'current'", (survey_id,))
            survey = cursor.fetchone()
            
            if not survey:
                flash('Survey not found or not available!', 'error')
                return redirect(url_for('available_surveys'))
            
            # Get questions and options
            cursor.execute("""
                SELECT sq.*, so.option_text, so.option_order
                FROM survey_questions sq
                LEFT JOIN survey_options so ON sq.id = so.question_id
                WHERE sq.survey_id = %s
                ORDER BY sq.question_order, so.option_order
            """, (survey_id,))
            
            results = cursor.fetchall()
            
            # Group questions with their options
            questions = {}
            for row in results:
                q_id = row['id']
                if q_id not in questions:
                    questions[q_id] = {
                        'id': row['id'],
                        'text': row['question_text'],
                        'type': row['question_type'],
                        'order': row['question_order'],
                        'options': []
                    }
                
                if row['option_text']:
                    questions[q_id]['options'].append(row['option_text'])
            
            questions_list = sorted(questions.values(), key=lambda x: x['order'])
            
            return render_template('participant/take_survey.html', survey=survey, questions=questions_list)
    finally:
        connection.close()

@app.route('/participant/submit_survey', methods=['POST'])
@login_required
def participant_submit_survey():  # Renamed function to avoid conflict
    data = request.get_json()
    survey_id = data['survey_id']
    responses = data['responses']
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if already completed
            cursor.execute("""
                SELECT id FROM survey_completions 
                WHERE survey_id = %s AND participant_id = %s
            """, (survey_id, session['user_id']))
            
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Survey already completed!'})
            
            # Get survey details
            cursor.execute("SELECT * FROM surveys WHERE id = %s", (survey_id,))
            survey = cursor.fetchone()
            
            # Save responses
            for question_id, response in responses.items():
                if isinstance(response, list):
                    response_data = json.dumps(response)
                    response_text = None
                else:
                    response_data = None
                    response_text = response
                
                cursor.execute("""
                    INSERT INTO survey_responses (survey_id, participant_id, question_id, response_text, selected_options)
                    VALUES (%s, %s, %s, %s, %s)
                """, (survey_id, session['user_id'], question_id, response_text, response_data))
            
            # Mark as completed
            cursor.execute("""
                INSERT INTO survey_completions (survey_id, participant_id, tokens_earned)
                VALUES (%s, %s, %s)
            """, (survey_id, session['user_id'], survey['reward_tokens']))
            
            # Add to payout details if there are rewards
            if survey['reward_tokens'] > 0:
                cursor.execute("""
                    INSERT INTO payout_details (participant_id, survey_id, tokens_earned)
                    VALUES (%s, %s, %s)
                """, (session['user_id'], survey_id, survey['reward_tokens']))
            
            connection.commit()
            return jsonify({'success': True, 'message': 'Survey submitted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        connection.close()

@app.route('/participant/payout_details')
@login_required
def payout_details():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get total tokens
            cursor.execute("""
                SELECT COALESCE(SUM(tokens_earned), 0) as total_tokens
                FROM payout_details 
                WHERE participant_id = %s
            """, (session['user_id'],))
            total_tokens = cursor.fetchone()['total_tokens']
            
            # Get payout history
            cursor.execute("""
                SELECT pd.*, s.name as survey_name
                FROM payout_details pd
                JOIN surveys s ON pd.survey_id = s.id
                WHERE pd.participant_id = %s
                ORDER BY pd.earned_at DESC
            """, (session['user_id'],))
            payouts = cursor.fetchall()
            
            return render_template('participant/payout_details.html', 
                                 total_tokens=total_tokens, payouts=payouts)
    finally:
        connection.close()

@app.route('/participant/help')
@login_required
def help_page():
    return render_template('participant/help.html')

@app.route('/participant/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password_hash FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                
                if check_password_hash(user['password_hash'], current_password):
                    new_hash = generate_password_hash(new_password)
                    cursor.execute("""
                        UPDATE users SET password_hash = %s WHERE id = %s
                    """, (new_hash, session['user_id']))
                    connection.commit()
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Current password is incorrect!', 'error')
        finally:
            connection.close()
    
    return render_template('auth/reset_password.html')

if __name__ == '__main__':
    app.run(debug=True)