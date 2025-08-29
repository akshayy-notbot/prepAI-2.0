// Onboarding JavaScript for PrepAI Multi-Page System

// Initialize onboarding when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    // Onboarding page initialized
    
    // Check if user can access this page
    if (!validatePageAccess()) {
        return;
    }
    
    // Add back button
    addBackButton();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load existing configuration if any
    loadExistingConfiguration();
    
    // Update UI based on current state
    updateOnboardingUI();
});

// Validate if user can access this page
function validatePageAccess() {
    if (!window.prepAIState) {
        console.error('❌ State management not loaded');
        return false;
    }
    
    // User should always be able to access onboarding
    return true;
}

// Add back button to return to homepage
function addBackButton() {
    if (window.PrepAIUtils && window.PrepAIUtils.UI) {
        window.PrepAIUtils.UI.createBackButton('index', document.body);
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
            window.location.href = 'index.html';
        });
        
        document.body.appendChild(backBtn);
    }
}

// Setup all event listeners for the onboarding page
function setupEventListeners() {
    console.log('🔧 Setting up event listeners...');
    
    // Role selection buttons
    const roleButtons = document.querySelectorAll('.role-btn');
    console.log(`📋 Found ${roleButtons.length} role buttons:`, roleButtons);
    
    roleButtons.forEach((btn, index) => {
        console.log(`🔘 Role button ${index}:`, btn.dataset.value, btn);
        btn.addEventListener('click', () => {
            console.log('🎯 Role button clicked:', btn.dataset.value);
            handleRoleSelect(btn.dataset.value);
        });
    });
    
    // Experience selection buttons
    const experienceButtons = document.querySelectorAll('.experience-btn');
    console.log(`📋 Found ${experienceButtons.length} experience buttons:`, experienceButtons);
    
    experienceButtons.forEach(btn => {
        btn.addEventListener('click', () => handleExperienceSelect(btn.dataset.value));
    });
    
    // Continue button
    const continueBtn = document.getElementById('onboarding-continue-btn');
    if (continueBtn) {
        continueBtn.addEventListener('click', handleContinueToDashboard);
        console.log('✅ Continue button event listener added');
    } else {
        console.error('❌ Continue button not found!');
    }
    
    console.log('✅ Onboarding event listeners setup complete');
}

// Load existing configuration from state
function loadExistingConfiguration() {
    if (!window.prepAIState) return;
    
    const config = window.prepAIState.interviewConfig;
    if (config.role || config.seniority || config.skills) {
        // Loading existing configuration
        
        // Restore role selection
        if (config.role) {
            updateRoleSelection(config.role);
        }
        
        // Restore seniority selection
        if (config.seniority) {
            updateSenioritySelection(config.seniority);
        }
        
        // Restore skills selection
        if (config.skills && config.skills.length > 0) {
            updateSkillsSelection(config.skills[0]);
        }
    }
}

// Handle role selection
function handleRoleSelect(role) {
    console.log('🎯 Role selected:', role);
    
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    // Update state
    window.prepAIState.updateInterviewConfig({
        role: role,
        seniority: null, // Clear subsequent selections
        skills: []
    });
    
    // Update UI
    updateRoleSelection(role);
    updateOnboardingUI();
}

// Update role selection in UI
function updateRoleSelection(role) {
    // Clear all role selections
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select the chosen role
    const selectedBtn = document.querySelector(`[data-value="${role}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('selected');
    }
}

// Handle experience/seniority selection
function handleExperienceSelect(level) {
    console.log('🎯 Experience level selected:', level);
    
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    // Update state
    window.prepAIState.updateInterviewConfig({
        seniority: level,
        skills: [] // Clear skills when seniority changes
    });
    
    // Update UI
    updateSenioritySelection(level);
    updateOnboardingUI();
}

// Update seniority selection in UI
function updateSenioritySelection(level) {
    // Clear all experience selections
    document.querySelectorAll('.experience-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select the chosen experience level
    const selectedBtn = document.querySelector(`[data-value="${level}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('selected');
    }
}

// Handle skill selection
function handleSkillSelection(selectedSkill) {
    console.log('🎯 Skill selected:', selectedSkill);
    
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    // Clear previous skill selections
    document.querySelectorAll('.skill-brick').forEach(brick => {
        brick.classList.remove('selected');
    });
    
    // Select new skill
    const selectedBrick = document.querySelector(`[data-skill="${selectedSkill}"]`);
    if (selectedBrick) {
        selectedBrick.classList.add('selected');
    }
    
    // Extract skill name and description
    const skillName = selectedSkill.split(' (')[0];
    const skillDescription = selectedSkill.includes('(') ? 
        selectedSkill.substring(selectedSkill.indexOf('(') + 1, selectedSkill.lastIndexOf(')')) : '';
    
    // Update state
    window.prepAIState.updateInterviewConfig({
        skills: [selectedSkill],
        selectedSkillName: skillName,
        selectedSkillDescription: skillDescription
    });
    
    updateOnboardingUI();
}

// Update skills selection in UI
function updateSkillsSelection(skill) {
    // Clear all skill selections
    document.querySelectorAll('.skill-brick').forEach(brick => {
        brick.classList.remove('selected');
    });
    
    // Select the chosen skill
    const selectedBrick = document.querySelector(`[data-skill="${skill}"]`);
    if (selectedBrick) {
        selectedBrick.classList.add('selected');
    }
}

// Update the onboarding UI based on current selections
function updateOnboardingUI() {
    if (!window.prepAIState) return;
    
    const config = window.prepAIState.interviewConfig;
    const roleSection = document.getElementById('role-section');
    const experienceSection = document.getElementById('experience-section');
    const skillsSection = document.getElementById('skills-section');
    const continueBtn = document.getElementById('onboarding-continue-btn');
    
    // Update role section styling
    if (config.role) {
        roleSection.classList.add('selected');
        roleSection.classList.remove('unselected');
        
        // Show experience section when role is selected
        experienceSection.classList.remove('hidden');
        experienceSection.classList.remove('disabled');
    } else {
        roleSection.classList.remove('selected');
        roleSection.classList.add('unselected');
        
        // Hide experience section when no role is selected
        experienceSection.classList.add('hidden');
        experienceSection.classList.add('disabled');
    }
    
    // Update experience section styling
    if (config.role && config.seniority) {
        experienceSection.classList.add('selected');
        experienceSection.classList.remove('unselected');
        
        // Show skills section when seniority is selected
        skillsSection.classList.remove('hidden');
        
        // Populate skills options
        populateSkillsOptions();
    } else {
        experienceSection.classList.remove('selected');
        experienceSection.classList.add('unselected');
        
        // Hide skills section when no seniority is selected
        skillsSection.classList.add('hidden');
    }
    
    // Update skills section
    if (config.role && config.seniority && config.skills && config.skills.length === 1) {
        skillsSection.classList.add('selected');
        skillsSection.classList.remove('unselected');
    } else {
        skillsSection.classList.remove('selected');
        skillsSection.classList.add('unselected');
    }
    
    // Enable/disable continue button
    if (config.role && config.seniority && config.skills && config.skills.length === 1) {
        continueBtn.disabled = false;
        continueBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
        continueBtn.disabled = true;
        continueBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
}

// Populate skills options based on role and seniority
function populateSkillsOptions() {
    if (!window.prepAIState || !window.PrepAIUtils) return;
    
    const config = window.prepAIState.interviewConfig;
    const skillsContainer = document.getElementById('skills-options');
    
    if (!config.role || !config.seniority) {
        skillsContainer.innerHTML = '<p class="text-gray-500 text-center py-4">Please select a role and experience level first.</p>';
        return;
    }

    const skills = window.PrepAIUtils.SkillsMapping.getSkillsByRoleAndSeniority(config.role, config.seniority);
    
    skillsContainer.innerHTML = skills.map(skill => {
        const isSelected = config.skills && config.skills.includes(skill);
        const selectedClass = isSelected ? 'selected' : '';
        
        // Extract skill name and description for display
        const skillName = skill.split(' (')[0];
        const skillDescription = skill.includes('(') ? 
            skill.substring(skill.indexOf('(') + 1, skill.lastIndexOf(')')) : '';
        
        return `
            <button type="button" 
                    class="skill-brick choice-button p-4 bg-gray-100 rounded-lg text-left transition-all duration-200 ${selectedClass}" 
                    data-skill="${skill}">
                <h4 class="font-semibold text-gray-800">${skillName}</h4>
                ${skillDescription ? `<p class="text-sm text-gray-600 mt-1">${skillDescription}</p>` : ''}
            </button>
        `;
    }).join('');
    
    // Add event listeners to all skill bricks
    const skillBricks = skillsContainer.querySelectorAll('.skill-brick');
    skillBricks.forEach(brick => {
        brick.addEventListener('click', function() {
            handleSkillSelection(this.dataset.skill);
        });
    });
}

// Handle continue to dashboard
function handleContinueToDashboard() {
    if (!window.prepAIState) {
        console.error('❌ State management not available');
        return;
    }
    
    const config = window.prepAIState.interviewConfig;
    const validation = window.PrepAIUtils?.Validation?.validateInterviewConfig(config);
    
    if (validation && !validation.isValid) {
        console.error('❌ Invalid configuration:', validation.errors);
        return;
    }
    
    console.log('✅ Configuration complete, navigating to dashboard');
    
    // Navigate to dashboard
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('dashboard');
    } else {
        // Fallback navigation
        window.location.href = 'dashboard.html';
    }
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        handleRoleSelect, 
        handleExperienceSelect, 
        handleSkillSelection,
        handleContinueToDashboard
    };
}
