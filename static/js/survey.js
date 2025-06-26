// Survey creation and management
let questionCount = 0;

function addQuestion() {
    questionCount++;
    const questionsContainer = document.getElementById('questions-container');
    
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question-container';
    questionDiv.id = `question-${questionCount}`;
    
    questionDiv.innerHTML = `
        <div class="question-header">
            <div class="question-number">${questionCount}</div>
            <button type="button" class="question-remove" onclick="removeQuestion(${questionCount})">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div class="form-group">
            <label class="form-label">Question Text</label>
            <textarea class="form-textarea" name="question_text_${questionCount}" 
                     placeholder="Enter your question here..." required></textarea>
        </div>
        
        <div class="form-group">
            <label class="form-label">Question Type</label>
            <select class="form-select" name="question_type_${questionCount}" 
                    onchange="handleQuestionTypeChange(${questionCount})" required>
                <option value="">Select question type</option>
                <option value="radio">Radio Button</option>
                <option value="checkbox">Check Box</option>
                <option value="text">Descriptive</option>
            </select>
        </div>
        
        <div id="options-container-${questionCount}" class="options-container" style="display: none;">
            <label class="form-label">Answer Options</label>
            <div id="options-list-${questionCount}"></div>
            <button type="button" class="add-option-btn" onclick="addOption(${questionCount})">
                <i class="fas fa-plus"></i> Add Option
            </button>
        </div>
    `;
    
    questionsContainer.appendChild(questionDiv);
    questionDiv.scrollIntoView({ behavior: 'smooth' });
}

function removeQuestion(questionId) {
    const questionDiv = document.getElementById(`question-${questionId}`);
    if (questionDiv) {
        questionDiv.remove();
        renumberQuestions();
    }
}

function renumberQuestions() {
    const questions = document.querySelectorAll('.question-container');
    questions.forEach((question, index) => {
        const number = index + 1;
        const numberElement = question.querySelector('.question-number');
        if (numberElement) {
            numberElement.textContent = number;
        }
    });
}

function handleQuestionTypeChange(questionId) {
    const select = document.querySelector(`select[name="question_type_${questionId}"]`);
    const optionsContainer = document.getElementById(`options-container-${questionId}`);
    
    if (select.value === 'radio' || select.value === 'checkbox') {
        optionsContainer.style.display = 'block';
        if (document.getElementById(`options-list-${questionId}`).children.length === 0) {
            addOption(questionId);
            addOption(questionId);
        }
    } else {
        optionsContainer.style.display = 'none';
    }
}

function addOption(questionId) {
    const optionsList = document.getElementById(`options-list-${questionId}`);
    const optionCount = optionsList.children.length + 1;
    
    const optionDiv = document.createElement('div');
    optionDiv.className = 'option-container';
    optionDiv.innerHTML = `
        <input type="text" class="option-input" name="option_${questionId}_${optionCount}" 
               placeholder="Option ${optionCount}" required>
        <button type="button" class="option-remove" onclick="removeOption(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    optionsList.appendChild(optionDiv);
}

function removeOption(button) {
    const optionContainer = button.parentElement;
    const optionsList = optionContainer.parentElement;
    
    if (optionsList.children.length > 2) {
        optionContainer.remove();
        renumberOptions(optionsList);
    } else {
        showNotification('At least 2 options are required for multiple choice questions.', 'warning');
    }
}

function renumberOptions(optionsList) {
    const options = optionsList.querySelectorAll('.option-input');
    options.forEach((option, index) => {
        option.placeholder = `Option ${index + 1}`;
    });
}

function createSurvey() {
    const form = document.getElementById('survey-form');
    const formData = new FormData(form);
    
    // Validate form
    if (!validateSurveyForm()) {
        return;
    }
    
    // Collect survey data
    const surveyData = {
        survey_name: formData.get('survey_name'),
        survey_type: formData.get('survey_type'),
        reward_tokens: parseInt(formData.get('reward_tokens')) || 0,
        start_time: formData.get('start_time') || null,
        questions: []
    };
    
    // Collect questions
    const questions = document.querySelectorAll('.question-container');
    questions.forEach((questionDiv, index) => {
        const questionId = index + 1;
        const questionText = questionDiv.querySelector(`textarea[name="question_text_${questionId}"]`).value;
        const questionType = questionDiv.querySelector(`select[name="question_type_${questionId}"]`).value;
        
        const question = {
            text: questionText,
            type: questionType,
            options: []
        };
        
        if (questionType === 'radio' || questionType === 'checkbox') {
            const options = questionDiv.querySelectorAll(`input[name^="option_${questionId}_"]`);
            options.forEach(option => {
                if (option.value.trim()) {
                    question.options.push(option.value.trim());
                }
            });
        }
        
        surveyData.questions.push(question);
    });
    
    // Submit survey
    fetch('/admin/submit_survey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(surveyData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        showNotification('An error occurred while creating the survey.', 'error');
        console.error('Error:', error);
    });
}

function validateSurveyForm() {
    const surveyName = document.querySelector('input[name="survey_name"]').value.trim();
    const surveyType = document.querySelector('select[name="survey_type"]').value;
    const questions = document.querySelectorAll('.question-container');
    
    if (!surveyName) {
        showNotification('Please enter a survey name.', 'error');
        return false;
    }
    
    if (!surveyType) {
        showNotification('Please select a survey type.', 'error');
        return false;
    }
    
    if (questions.length === 0) {
        showNotification('Please add at least one question.', 'error');
        return false;
    }
    
    // Validate each question
    for (let i = 0; i < questions.length; i++) {
        const questionDiv = questions[i];
        const questionId = i + 1;
        const questionText = questionDiv.querySelector(`textarea[name="question_text_${questionId}"]`).value.trim();
        const questionType = questionDiv.querySelector(`select[name="question_type_${questionId}"]`).value;
        
        if (!questionText) {
            showNotification(`Please enter text for question ${questionId}.`, 'error');
            return false;
        }
        
        if (!questionType) {
            showNotification(`Please select a type for question ${questionId}.`, 'error');
            return false;
        }
        
        if (questionType === 'radio' || questionType === 'checkbox') {
            const options = questionDiv.querySelectorAll(`input[name^="option_${questionId}_"]`);
            let validOptions = 0;
            
            options.forEach(option => {
                if (option.value.trim()) {
                    validOptions++;
                }
            });
            
            if (validOptions < 2) {
                showNotification(`Please provide at least 2 options for question ${questionId}.`, 'error');
                return false;
            }
        }
    }
    
    return true;
}

// Survey taking functionality
function submitSurvey() {
    const surveyId = document.getElementById('survey-id').value;
    const responses = {};
    
    // Collect responses
    const questions = document.querySelectorAll('.survey-question');
    let allAnswered = true;
    
    questions.forEach(questionDiv => {
        const questionId = questionDiv.dataset.questionId;
        const questionType = questionDiv.dataset.questionType;
        
        if (questionType === 'radio') {
            const selected = questionDiv.querySelector('input[type="radio"]:checked');
            if (selected) {
                responses[questionId] = selected.value;
            } else {
                allAnswered = false;
            }
        } else if (questionType === 'checkbox') {
            const selected = questionDiv.querySelectorAll('input[type="checkbox"]:checked');
            if (selected.length > 0) {
                responses[questionId] = Array.from(selected).map(cb => cb.value);
            } else {
                allAnswered = false;
            }
        } else if (questionType === 'text') {
            const textArea = questionDiv.querySelector('textarea');
            if (textArea.value.trim()) {
                responses[questionId] = textArea.value.trim();
            } else {
                allAnswered = false;
            }
        }
    });
    
    if (!allAnswered) {
        showNotification('Please answer all questions before submitting.', 'warning');
        return;
    }
    
    // Submit responses
    fetch('/participant/submit_survey', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            survey_id: surveyId,
            responses: responses
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/participant/available_surveys';
            }, 2000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        showNotification('An error occurred while submitting the survey.', 'error');
        console.error('Error:', error);
    });
}

// Update time remaining displays
function updateTimeRemaining() {
    const timeElements = document.querySelectorAll('[data-end-time]');
    timeElements.forEach(element => {
        const endTime = element.dataset.endTime;
        element.textContent = formatTimeRemaining(endTime);
    });
}

// Update time remaining every minute
setInterval(updateTimeRemaining, 60000);
document.addEventListener('DOMContentLoaded', updateTimeRemaining);