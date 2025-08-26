// Dashboard JavaScript for PrepAI Multi-Page System

// Initialize dashboard when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard page initialized');
    
    // Check if user can access this page
    if (!validatePageAccess()) {
        return;
    }
    
    // Add back button
    addBackButton();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load and display configuration
    loadConfiguration();
    
    // Update dashboard display
    updateDashboardDisplay();
});

// Validate if user can access this page
function validatePageAccess() {
    if (!window.prepAIState) {
        console.error('❌ State management not loaded');
        return false;
    }
    
    // Check if user has complete configuration
    if (!window.prepAIState.canProceedTo('dashboard')) {
        console.warn('⚠️ User cannot access dashboard, redirecting to onboarding');
        if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
            window.PrepAIUtils.Navigation.goTo('onboarding');
        } else {
            window.location.href = 'onboarding.html';
        }
        return false;
    }
    
    return true;
}

// Add back button to return to onboarding
function addBackButton() {
    if (window.PrepAIUtils && window.PrepAIUtils.UI) {
        window.PrepAIUtils.UI.createBackButton('onboarding', document.body);
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
            window.location.href = 'onboarding.html';
        });
        
        document.body.appendChild(backBtn);
    }
}

// Setup all event listeners for the dashboard page
function setupEventListeners() {
    // Edit configuration button
    const editConfigBtn = document.getElementById('edit-config-btn');
    if (editConfigBtn) {
        editConfigBtn.addEventListener('click', handleEditConfiguration);
    }
    
    // Start interview button
    const startInterviewBtn = document.getElementById('start-interview-btn');
    if (startInterviewBtn) {
        startInterviewBtn.addEventListener('click', handleStartInterview);
    }
    
    // Go to interview prep button
    const goToInterviewPrepBtn = document.getElementById('go-to-interview-prep-btn');
    if (goToInterviewPrepBtn) {
        goToInterviewPrepBtn.addEventListener('click', handleStartInterview);
    }
    
    console.log('✅ Dashboard event listeners setup complete');
}

// Load configuration from state
function loadConfiguration() {
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    const config = window.prepAIState.interviewConfig;
    console.log('🔍 Loading configuration:', config);
    
    // Validate configuration
    if (window.PrepAIUtils && window.PrepAIUtils.Validation) {
        const validation = window.PrepAIUtils.Validation.validateInterviewConfig(config);
        if (!validation.isValid) {
            console.error('❌ Invalid configuration:', validation.errors);
            // Redirect to onboarding to fix configuration
            if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
                window.PrepAIUtils.Navigation.goTo('onboarding');
            } else {
                window.location.href = 'onboarding.html';
            }
            return;
        }
    }
}

// Update dashboard display with configuration data
function updateDashboardDisplay() {
    if (!window.prepAIState) return;
    
    const config = window.prepAIState.interviewConfig;
    
    // Update role and company display
    const roleCompanyElement = document.getElementById('dashboard-role-company');
    if (roleCompanyElement && config.role && config.seniority) {
        roleCompanyElement.textContent = `For a ${config.role} role (${config.seniority} level).`;
    }
    
    // Update skills list
    const skillsListElement = document.getElementById('key-skills-list');
    if (skillsListElement && config.skills && config.skills.length > 0) {
        skillsListElement.innerHTML = config.skills.map(skill => {
            const skillName = skill.split(' (')[0];
            const skillDescription = skill.includes('(') ? 
                skill.substring(skill.indexOf('(') + 1, skill.lastIndexOf(')')) : '';
            return `<li><strong>${skillName}</strong>${skillDescription ? ` - ${skillDescription}` : ''}</li>`;
        }).join('');
    }
    
    console.log('✅ Dashboard display updated');
}

// Handle edit configuration button click
function handleEditConfiguration() {
    console.log('✏️ Edit configuration clicked');
    
    // Navigate to onboarding page
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('onboarding');
    } else {
        // Fallback navigation
        window.location.href = 'onboarding.html';
    }
}

// Handle start interview button click
function handleStartInterview() {
    console.log('🚀 Start interview clicked');
    
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
    
    // Navigate to interview prep page
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('interview-prep');
    } else {
        // Fallback navigation
        window.location.href = 'interview-prep.html';
    }
}

// Add some interactive elements for better UX
function addInteractiveElements() {
    // No hover animations - keeping professional, modern UX
    console.log('✅ Professional UX mode enabled - no hover animations');
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    addInteractiveElements();
});

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        validatePageAccess, 
        loadConfiguration, 
        updateDashboardDisplay,
        handleEditConfiguration,
        handleStartInterview
    };
}
