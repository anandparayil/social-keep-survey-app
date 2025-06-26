// Authentication related functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeAuthForms();
});

function initializeAuthForms() {
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.name === 'password' && input.form.action.includes('register')) {
            addPasswordStrengthIndicator(input);
        }
    });
    
    // Form validation
    const authForms = document.querySelectorAll('form');
    authForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateAuthForm(this)) {
                e.preventDefault();
            }
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

function addPasswordStrengthIndicator(passwordInput) {
    const strengthIndicator = document.createElement('div');
    strengthIndicator.className = 'password-strength';
    strengthIndicator.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill"></div>
        </div>
        <div class="strength-text">Password strength: <span>Weak</span></div>
    `;
    
    passwordInput.parentNode.appendChild(strengthIndicator);
    
    passwordInput.addEventListener('input', function() {
        updatePasswordStrength(this.value, strengthIndicator);
    });
}

function updatePasswordStrength(password, indicator) {
    const strength = calculatePasswordStrength(password);
    const fill = indicator.querySelector('.strength-fill');
    const text = indicator.querySelector('.strength-text span');
    
    // Update visual indicator
    fill.style.width = `${strength.percentage}%`;
    fill.className = `strength-fill strength-${strength.level}`;
    text.textContent = strength.label;
    text.className = `strength-${strength.level}`;
}

function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];
    
    // Length check
    if (password.length >= 8) score += 25;
    else feedback.push('At least 8 characters');
    
    // Uppercase check
    if (/[A-Z]/.test(password)) score += 25;
    else feedback.push('One uppercase letter');
    
    // Lowercase check
    if (/[a-z]/.test(password)) score += 25;
    else feedback.push('One lowercase letter');
    
    // Number or special character check
    if (/[\d\W]/.test(password)) score += 25;
    else feedback.push('One number or special character');
    
    let level, label;
    if (score < 50) {
        level = 'weak';
        label = 'Weak';
    } else if (score < 75) {
        level = 'medium';
        label = 'Medium';
    } else if (score < 100) {
        level = 'strong';
        label = 'Strong';
    } else {
        level = 'very-strong';
        label = 'Very Strong';
    }
    
    return {
        score,
        percentage: score,
        level,
        label,
        feedback
    };
}

function validateAuthForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('.form-control, .form-select');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Additional validation for registration form
    if (form.action.includes('register')) {
        const password = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');
        
        if (confirmPassword && password.value !== confirmPassword.value) {
            showFieldError(confirmPassword, 'Passwords do not match');
            isValid = false;
        }
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Password validation
    if (field.type === 'password' && field.name === 'password' && value) {
        const strength = calculatePasswordStrength(value);
        if (strength.score < 50) {
            showFieldError(field, 'Password is too weak');
            isValid = false;
        }
    }
    
    // Username validation
    if (field.name === 'username' && value) {
        if (value.length < 3) {
            showFieldError(field, 'Username must be at least 3 characters');
            isValid = false;
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            showFieldError(field, 'Username can only contain letters, numbers, and underscores');
            isValid = false;
        }
    }
    
    if (isValid) {
        clearFieldError(field);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    
    const existingError = field.parentNode.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
}

// Add password strength CSS
const strengthStyle = document.createElement('style');
strengthStyle.textContent = `
    .password-strength {
        margin-top: 10px;
    }
    
    .strength-bar {
        height: 4px;
        background: #e9ecef;
        border-radius: 2px;
        overflow: hidden;
        margin-bottom: 5px;
    }
    
    .strength-fill {
        height: 100%;
        transition: all 0.3s ease;
        border-radius: 2px;
    }
    
    .strength-weak { background: #dc3545; }
    .strength-medium { background: #ffc107; }
    .strength-strong { background: #28a745; }
    .strength-very-strong { background: #17a2b8; }
    
    .strength-text {
        font-size: 0.85rem;
        color: #666;
    }
    
    .strength-text .strength-weak { color: #dc3545; }
    .strength-text .strength-medium { color: #ffc107; }
    .strength-text .strength-strong { color: #28a745; }
    .strength-text .strength-very-strong { color: #17a2b8; }
`;
document.head.appendChild(strengthStyle);