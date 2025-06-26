// Dashboard specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Update real-time data every 30 seconds
    setInterval(updateDashboardData, 30000);
});

function initializeDashboard() {
    // Add hover effects to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Initialize quick action buttons
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Load dashboard statistics
    loadDashboardStats();
}

function loadDashboardStats() {
    // This would typically fetch real-time statistics from the server
    // For now, we'll simulate with static data
    
    const userType = document.body.dataset.userType;
    
    if (userType === 'admin') {
        loadAdminStats();
    } else {
        loadParticipantStats();
    }
}

function loadAdminStats() {
    // Simulate loading admin statistics
    const stats = {
        totalSurveys: 12,
        activeSurveys: 5,
        totalParticipants: 48,
        completionRate: 78
    };
    
    updateStatCards(stats);
}

function loadParticipantStats() {
    // Simulate loading participant statistics
    const stats = {
        availableSurveys: 3,
        completedSurveys: 8,
        totalTokens: 45,
        upcomingSurveys: 2
    };
    
    updateStatCards(stats);
}

function updateStatCards(stats) {
    // Update stat cards with real data
    Object.keys(stats).forEach(key => {
        const statElement = document.querySelector(`[data-stat="${key}"]`);
        if (statElement) {
            animateNumber(statElement, stats[key]);
        }
    });
}

function animateNumber(element, targetNumber) {
    const startNumber = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = Date.now();
    
    function updateNumber() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentNumber = Math.floor(startNumber + (targetNumber - startNumber) * progress);
        element.textContent = currentNumber;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function updateDashboardData() {
    // Update time-sensitive data like survey deadlines
    updateTimeRemaining();
    
    // Refresh notification counts
    updateNotificationCounts();
}

function updateNotificationCounts() {
    // Update notification badges for new surveys, messages, etc.
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            const notificationBadges = document.querySelectorAll('.notification-badge');
            notificationBadges.forEach(badge => {
                const type = badge.dataset.type;
                if (data[type] && data[type] > 0) {
                    badge.textContent = data[type];
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            });
        })
        .catch(error => {
            console.log('Notification update failed:', error);
        });
}

// Add ripple effect CSS
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);