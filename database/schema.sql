CREATE DATABASE IF NOT EXISTS social;
USE social;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'participant') NOT NULL,
    is_activated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE surveys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    survey_type ENUM('daily', 'biweekly') NOT NULL,
    status ENUM('upcoming', 'current', 'closed') DEFAULT 'upcoming',
    start_time DATETIME,
    end_time DATETIME,
    reward_tokens INT DEFAULT 0,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE survey_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    question_text TEXT NOT NULL,
    question_type ENUM('radio', 'checkbox', 'text') NOT NULL,
    question_order INT,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
);

CREATE TABLE survey_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT,
    option_text VARCHAR(500) NOT NULL,
    option_order INT,
    FOREIGN KEY (question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
);

CREATE TABLE survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    participant_id INT,
    question_id INT,
    response_text TEXT,
    selected_options JSON,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id),
    FOREIGN KEY (participant_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
);

CREATE TABLE survey_completions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    participant_id INT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_earned INT DEFAULT 0,
    FOREIGN KEY (survey_id) REFERENCES surveys(id),
    FOREIGN KEY (participant_id) REFERENCES users(id),
    UNIQUE KEY unique_completion (survey_id, participant_id)
);

CREATE TABLE payout_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    participant_id INT,
    survey_id INT,
    tokens_earned INT,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participant_id) REFERENCES users(id),
    FOREIGN KEY (survey_id) REFERENCES surveys(id)
);

CREATE TABLE survey_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_name VARCHAR(200) NOT NULL,
    survey_type ENUM('daily', 'biweekly') NOT NULL,
    scheduled_date DATETIME NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
