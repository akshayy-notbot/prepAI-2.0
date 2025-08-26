// Homepage JavaScript for PrepAI Multi-Page System

// Initialize homepage when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏠 Homepage initialized');
    
    // Check if user has existing configuration and redirect if appropriate
    checkExistingConfiguration();
    
    // Setup event listeners
    setupEventListeners();
});

// Check if user has existing configuration and redirect appropriately
function checkExistingConfiguration() {
    if (!window.prepAIState) {
        console.warn('⚠️ State management not loaded, skipping configuration check');
        return;
    }
    
    const stateSummary = window.prepAIState.getStateSummary();
    console.log('🔍 Current state summary:', stateSummary);
    
    // If user has complete configuration, redirect to dashboard
    if (stateSummary.isComplete) {
        console.log('✅ User has complete configuration, redirecting to dashboard');
        // Small delay to ensure page is fully loaded
        setTimeout(() => {
            window.PrepAIUtils.Navigation.goTo('dashboard');
        }, 100);
    }
}

// Setup all event listeners for the homepage
function setupEventListeners() {
    // Start onboarding button
    const startOnboardingBtn = document.getElementById('start-onboarding-btn');
    if (startOnboardingBtn) {
        startOnboardingBtn.addEventListener('click', handleStartOnboarding);
        console.log('✅ Start onboarding button event listener added');
    } else {
        console.error('❌ Start onboarding button not found!');
    }
}

// Handle start onboarding button click
function handleStartOnboarding() {
    console.log('🚀 Start onboarding button clicked!');
    
    // Reset any existing state to start fresh
    if (window.prepAIState) {
        window.prepAIState.resetState();
        console.log('🔄 State reset for new onboarding session');
    }
    
    // Navigate to onboarding page
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('onboarding');
    } else {
        // Fallback navigation
        console.warn('⚠️ Navigation utilities not available, using fallback');
        window.location.href = 'onboarding.html';
    }
}

// Add some interactive elements for better UX
function addInteractiveElements() {
    // No hover animations - keeping professional, modern UX
    console.log('✅ Professional UX mode enabled - no hover animations');
}

// Add smooth scroll behavior for better UX
function addSmoothScroll() {
    // Professional scroll behavior - no smooth animations
    console.log('✅ Professional scroll behavior enabled');
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    addInteractiveElements();
    addSmoothScroll();
});

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        checkExistingConfiguration, 
        setupEventListeners, 
        handleStartOnboarding 
    };
}
