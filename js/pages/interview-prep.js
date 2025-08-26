// Interview Prep JavaScript for PrepAI Multi-Page System

// Initialize interview prep when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    // Interview prep page initialized
    
    // Check if user can access this page
    if (!validatePageAccess()) {
        return;
    }
    
    // Add back button
    addBackButton();
    
    // Setup event listeners
    setupEventListeners();
    
    // Display configuration summary
    displayConfigurationSummary();
});

// Validate if user can access this page
function validatePageAccess() {
    if (!window.prepAIState) {
        console.error('❌ State management not loaded');
        return false;
    }
    
    // Check if user has complete configuration
    if (!window.prepAIState.canProceedTo('interview-prep')) {
        console.warn('⚠️ User cannot access interview prep, redirecting to onboarding');
        if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
            window.PrepAIUtils.Navigation.goTo('onboarding');
        } else {
            window.location.href = 'onboarding.html';
        }
        return false;
    }
    
    return true;
}

// Add back button to return to dashboard
function addBackButton() {
    if (window.PrepAIUtils && window.PrepAIUtils.UI) {
        window.PrepAIUtils.UI.createBackButton('dashboard', document.body);
    } else {
        // Fallback back button
        const backBtn = document.createElement('button');
        backBtn.className = 'back-btn flex items-center gap-2';
        backBtn.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            <span class="hidden sm:inline">Back</span>
        `;
        
        backBtn.addEventListener('click', () => {
            window.location.href = 'dashboard.html';
        });
        
        document.body.appendChild(backBtn);
    }
}

// Setup all event listeners for the interview prep page
function setupEventListeners() {
    // Start interview button
    const startInterviewBtn = document.getElementById('start-interview-btn');
    if (startInterviewBtn) {
        startInterviewBtn.addEventListener('click', handleStartInterview);
        // Start interview button event listener added
    } else {
        console.error('❌ Start interview button not found!');
    }
}

// Display configuration summary for user review
function displayConfigurationSummary() {
    if (!window.prepAIState) return;
    
    const config = window.prepAIState.interviewConfig;
    // Displaying configuration summary
    
    // You could add a configuration summary display here
    // For now, we'll just log it to console
    // Interview Configuration loaded
}

// Handle start interview button click
function handleStartInterview() {
    // Start interview clicked
    
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    // Validate configuration before proceeding
    const config = window.prepAIState.interviewConfig;
    if (window.PrepAIUtils && window.PrepAIUtils.Validation) {
        const validation = window.PrepAIUtils.Validation.validateInterviewConfig(config);
        if (!validation.isValid) {
            console.error('❌ Invalid configuration:', validation.errors);
            alert('Please complete your interview configuration first.');
            return;
        }
    }
    
    // Store the configuration in sessionStorage for the interview page
    try {
        sessionStorage.setItem('prepai_interview_config', JSON.stringify(config));
        console.log('✅ Configuration stored in sessionStorage');
    } catch (error) {
        console.error('❌ Error storing configuration:', error);
    }
    
    // Navigate to the interview page (keeping it as single page for UX)
    console.log('🎯 Starting interview with configuration:', config);
    
    // Navigate to our new interview page
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('interview');
    } else {
        // Fallback navigation
        window.location.href = 'interview.html';
    }
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        validatePageAccess, 
        displayConfigurationSummary,
        handleStartInterview
    };
}
