// --- Global State ---
let interviewId = null;
let sessionId = null;  // Store session ID from backend
let questions = [];
let currentQuestionIndex = 0;
let transcript = [];
let interviewConfig = {}; // To store user selections

let isWaitingForAI = false; // Track if we're waiting for AI response

// --- Screen & Element References ---
let screens = {}; // Will be initialized after DOM loads
let chatInput, chatWindow, feedbackOutput, sendBtn; // Will be initialized after DOM loads

// Initialize screens and other DOM elements after DOM loads
function initializeScreens() {
    screens = {
        homepage: document.getElementById('homepage-screen'),
        onboarding: document.getElementById('onboarding-screen'),
        dashboard: document.getElementById('dashboard-screen'),
        interviewPrep: document.getElementById('interview-prep-screen'),
        interview: document.getElementById('interview-screen'),
        analysis: document.getElementById('analysis-screen'),
        feedback: document.getElementById('feedback-screen'),
    };
    
    // Initialize other DOM elements
    chatInput = document.getElementById('chat-input');
    chatWindow = document.getElementById('chat-window');
    feedbackOutput = document.getElementById('feedback-output');
    sendBtn = document.getElementById('send-btn');
    
    console.log('✅ Screens initialized:', Object.keys(screens));
    console.log('✅ DOM elements initialized:', {
        chatInput: !!chatInput,
        chatWindow: !!chatWindow,
        feedbackOutput: !!feedbackOutput,
        sendBtn: !!sendBtn
    });
    
    // Setup event listeners after DOM elements are available
    setupEventListeners();
}

// Setup all event listeners
function setupEventListeners() {
    // Start onboarding button
    const startOnboardingBtn = document.getElementById('start-onboarding-btn');
    if (startOnboardingBtn) {
        startOnboardingBtn.addEventListener('click', () => {
            console.log('🚀 Start onboarding button clicked!');
            console.log('🔍 Current screens state:', screens);
            console.log('🔍 Attempting to show onboarding screen...');
            
            showScreen('onboarding');
            initializeOnboarding(); // Initialize the onboarding state
            
            console.log('✅ Onboarding screen should now be visible');
        });
        console.log('✅ Start onboarding button event listener added');
    } else {
        console.error('❌ Start onboarding button not found!');
    }
    
    // Setup chat-related event listeners only if elements exist
    if (sendBtn && chatInput) {
        console.log('✅ Setting up chat event listeners...');
        sendBtn.addEventListener('click', handleSubmitAnswer);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmitAnswer();
            }
        });
        console.log('✅ Chat event listeners setup complete');
    } else {
        console.warn('⚠️ Chat elements not found, skipping chat event listeners');
    }
    
    // Add debugging for exit button setup
    const exitButton = document.getElementById('end-interview-btn');
    if (exitButton) {
        console.log('✅ Exit button found, adding event listener...');
        exitButton.addEventListener('click', endInterview);
        console.log('✅ Exit button event listener added successfully');
    } else {
        console.error('❌ Exit button not found! Element ID: end-interview-btn');
        console.error('❌ Available elements with similar IDs:');
        document.querySelectorAll('[id*="end"], [id*="exit"], [id*="interview"]').forEach(el => {
            console.error('  -', el.id, el.tagName, el.className);
        });
    }
    
    console.log('✅ Event listeners setup complete');
}

// --- Helper Functions ---
function showScreen(screenKey) {
    if (Object.keys(screens).length === 0) {
        console.error('❌ Screens not yet initialized. Please wait for DOM to load.');
        return;
    }
    
    if (!screens[screenKey]) {
        console.error('❌ Screen not found:', screenKey);
        return;
    }
    
    // Clean up back buttons from all screens before switching
    Object.values(screens).forEach(screen => {
        if (screen) {
            cleanupBackButton(screen);
            screen.classList.add('hidden');
        }
    });
    
    if (screens[screenKey]) {
        screens[screenKey].classList.remove('hidden');
        
        // Add back buttons based on current screen
        switch (screenKey) {
            case 'onboarding':
                // Back to homepage
                addBackButton(screens[screenKey], 'homepage');
                break;
            case 'dashboard':
                // Back to onboarding
                addBackButton(screens[screenKey], 'onboarding');
                break;
            case 'interviewPrep':
                // Back to dashboard
                addBackButton(screens[screenKey], 'dashboard');
                break;
            case 'interview':
                // No back button during interview - prevent going back
                break;
            case 'analysis':
                // No back button during analysis
                break;
            case 'feedback':
                // No back button on feedback - can restart
                break;
        }
    }
}

// --- Configuration ---
// Use configuration from config.js with fallback
const BACKEND_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
const WS_BASE_URL = window.PREPAI_CONFIG?.WS_BASE_URL || 'wss://prepai-api.onrender.com';

// Log configuration for debugging
console.log('🔧 Configuration loaded:', {
    BACKEND_URL,
    WS_BASE_URL,
    PREPAI_CONFIG: window.PREPAI_CONFIG
});

// Configuration validation function
function validateConfiguration() {
    console.log('🔧 Validating configuration...');
    console.log('🔧 window.PREPAI_CONFIG exists:', !!window.PREPAI_CONFIG);
    console.log('🔧 window.PREPAI_CONFIG_FULL exists:', !!window.PREPAI_CONFIG_FULL);
    
    if (window.PREPAI_CONFIG) {
        console.log('🔧 Current config:', window.PREPAI_CONFIG);
        console.log('🔧 API_BASE_URL from config:', window.PREPAI_CONFIG.API_BASE_URL);
        console.log('🔧 WS_BASE_URL from config:', window.PREPAI_CONFIG.WS_BASE_URL);
    }
    
    console.log('🔧 Final BACKEND_URL:', BACKEND_URL);
    console.log('🔧 Final WS_BASE_URL:', WS_BASE_URL);
    
    // Check if we're using fallback values
    if (BACKEND_URL === 'https://prepai-api.onrender.com' && !window.PREPAI_CONFIG) {
        console.warn('⚠️ Using fallback BACKEND_URL - config.js may not be loaded properly');
    }
    
    if (WS_BASE_URL === 'wss://prepai-api.onrender.com' && !window.PREPAI_CONFIG) {
        console.warn('⚠️ Using fallback WS_BASE_URL - config.js may not be loaded properly');
    }
}

// Run configuration validation when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        validateConfiguration();
        initializeScreens();
        showScreen('homepage'); // Show homepage after screens are initialized
    });
} else {
    validateConfiguration();
    initializeScreens();
    showScreen('homepage'); // Show homepage after screens are initialized
}



// Simplified AI question handler (like your LLM code)
function handleAIQuestion(questionText) {
    console.log('🤖 AI Question received:', questionText);
    
    // Hide loading states
    hideQuestionLoading();
    hideInputLoadingStates();
    
    // Display the AI's question
    displayAIMessage(questionText);
    
    // Re-enable input (like your LLM code)
    enableChatInput();
    
    // Update status
    updateQuestionStatus('Question received');
    

}

function handleInterviewCompletion(message) {
    console.log('🎉 Interview completed:', message);
    
    // Display completion message
    displayAIMessage(message);
    
    // Disable input
    disableChatInput();
    
    // Update status
    updateQuestionStatus('Interview complete');
    

    
    // Show completion message
    setTimeout(() => {
        const completionMessage = document.createElement('div');
        completionMessage.className = 'text-center py-4 text-green-600 font-semibold';
        completionMessage.innerHTML = `
            <div class="flex items-center justify-center space-x-2">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>All interview goals have been covered!</span>
            </div>
        `;
        chatWindow.appendChild(completionMessage);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }, 1000);
}

function displayAIMessage(message) {
    // Use the message template from HTML for consistent styling
    const template = document.getElementById('message-template');
    if (template) {
        const messageElement = template.content.cloneNode(true);
        
        // Update the message content
        const contentDiv = messageElement.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.textContent = message;
        }
        
        // Add AI styling
        const messageBubble = messageElement.querySelector('.message-bubble');
        if (messageBubble) {
            messageBubble.classList.add('ai');
        }
        
        // Add timestamp
        const metaDiv = messageElement.querySelector('.message-meta');
        if (metaDiv) {
            metaDiv.textContent = new Date().toLocaleTimeString();
        }
        
        // Add to chat window
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Update transcript
        transcript.push({
            question: message,
            answer: null,
            timestamp: new Date().toISOString()
        });
        
    } else {
        // Fallback to simple method (like your LLM code)
        addMessageToChat(message, 'ai');
    }
}

// Enhanced addMessageToChat function with WhatsApp-style layout
function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message flex gap-3 mb-4';
    
    // Avatar and message alignment
    if (sender === 'user') {
        messageDiv.classList.add('justify-end'); // Align user messages to the right
    } else {
        messageDiv.classList.add('justify-start'); // Align AI messages to the left
    }
    
    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'flex-shrink-0';
    
    if (sender === 'user') {
        avatarDiv.innerHTML = `
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
            </div>
        `;
    } else {
        avatarDiv.innerHTML = `
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.6 73M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
            </div>
        `;
    }
    
    // Message bubble
    const messageBubble = document.createElement('div');
    messageBubble.className = 'flex-grow';
    messageBubble.innerHTML = `
        <div class="message-bubble ${sender === 'user' ? 'user' : 'ai'}">
            <div class="message-content leading-relaxed">${message}</div>
            <div class="message-meta text-xs text-gray-500 mt-2 font-mono">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    // For user messages, put avatar after the message bubble
    if (sender === 'user') {
        messageDiv.appendChild(messageBubble);
        messageDiv.appendChild(avatarDiv);
    } else {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(messageBubble);
    }
    
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function displayErrorMessage(message) {
    // Use the error template from HTML
    const template = document.getElementById('error-template');
    if (template) {
        const messageElement = template.content.cloneNode(true);
        
        // Update the message content
        const contentDiv = messageElement.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.textContent = message;
        }
        
        // Add retry functionality
        const retryBtn = messageElement.querySelector('.retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                // Remove the error message - use proper DOM removal for cloned nodes
                const messageContainer = retryBtn.closest('.message-container');
                if (messageContainer) {
                    messageContainer.remove();
                } else {
                    // Fallback: find the parent message element
                    const parentMessage = retryBtn.closest('.chat-message');
                    if (parentMessage) {
                        parentMessage.remove();
                    }
                }
                // Retry the last action
                retryLastAction();
            });
        }
        
        // Add to chat window
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
    } else {
        // Fallback to old method
        addMessageToChat(`Error: ${message}`, 'ai');
    }
}

function retryLastAction() {
    // Implement retry logic based on your needs
    console.log('🔄 Retrying last action...');
    // For now, just re-enable input
    enableChatInput();
}

function enableChatInput() {
    if (chatInput && sendBtn) {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
        isWaitingForAI = false;
        
        // Update status
        updateQuestionStatus('Ready for your answer');
    } else {
        console.warn('⚠️ Chat elements not available for enableChatInput');
    }
}

function disableChatInput() {
    if (chatInput && sendBtn) {
        chatInput.disabled = true;
        sendBtn.disabled = true;
        isWaitingForAI = true;
    } else {
        console.warn('⚠️ Chat elements not available for disableChatInput');
    }
}

function updateQuestionStatus(status) {
    const statusElement = document.getElementById('question-status');
    if (statusElement) {
        statusElement.textContent = status;
    }
}

function hideInputLoadingStates() {
    // Hide all loading indicators
    const typingIndicator = document.getElementById('typing-indicator');
    const processingIndicator = document.getElementById('processing-indicator');
    const successIndicator = document.getElementById('success-indicator');
    
    if (typingIndicator) typingIndicator.classList.add('hidden');
    if (processingIndicator) processingIndicator.classList.add('hidden');
    if (successIndicator) successIndicator.classList.add('hidden');
}

function showInputLoadingState(type) {
    // Hide all first
    hideInputLoadingStates();
    
    // Show the requested one
    switch (type) {
        case 'typing':
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) typingIndicator.classList.remove('hidden');
            break;
        case 'processing':
            const processingIndicator = document.getElementById('processing-indicator');
            if (processingIndicator) processingIndicator.classList.remove('hidden');
            break;
        case 'success':
            const successIndicator = document.getElementById('success-indicator');
            if (successIndicator) successIndicator.classList.remove('hidden');
            break;
    }
}

// --- Enhanced Onboarding Flow ---
// Event listeners are now set up in setupEventListeners() after DOM loads

// Handle role selection
function handleRoleSelect(role) {
    console.log('🎯 Role selected:', role);
    interviewConfig.role = role;
    // Clear subsequent selections when role changes
    interviewConfig.seniority = null;
    interviewConfig.skills = [];
    updateOnboardingUI();
}

// Handle experience/seniority selection
function handleExperienceSelect(level) {
    console.log('🎯 Experience level selected:', level);
    interviewConfig.seniority = level;
    // Clear skills when seniority changes
    interviewConfig.skills = [];
    updateOnboardingUI();
}

// Reset onboarding state
function resetOnboardingState() {
    interviewConfig.role = null;
    interviewConfig.seniority = null;
    interviewConfig.skills = [];
    updateOnboardingUI();
}

// Initialize onboarding state
function initializeOnboarding() {
    resetOnboardingState();
}

// Update the onboarding UI based on current selections
function updateOnboardingUI() {
    const roleSection = document.getElementById('role-section');
    const experienceSection = document.getElementById('experience-section');
    const skillsSection = document.getElementById('skills-section');
    const continueBtn = document.getElementById('onboarding-continue-btn');
    
    // Update role section styling and button states
    if (interviewConfig.role) {
        roleSection.classList.add('selected');
        roleSection.classList.remove('unselected');
        
        // Update role button states
        document.querySelectorAll('.role-btn').forEach(btn => {
            btn.classList.remove('selected');
            // Use data-value attribute for reliable matching
            const buttonValue = btn.getAttribute('data-value');
            if (buttonValue === interviewConfig.role) {
                btn.classList.add('selected');
            }
        });
        
        // Show experience section when role is selected
        experienceSection.classList.remove('hidden');
    } else {
        roleSection.classList.remove('selected');
        roleSection.classList.add('unselected');
        document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('selected'));
        
        // Hide experience section when no role is selected
        experienceSection.classList.add('hidden');
    }
    
    // Update experience section styling and enable/disable
    if (interviewConfig.role) {
        experienceSection.classList.remove('disabled');
        if (interviewConfig.seniority) {
            experienceSection.classList.add('selected');
            experienceSection.classList.remove('unselected');
            
            // Update experience button states
            document.querySelectorAll('.experience-btn').forEach(btn => {
                btn.classList.remove('selected');
                // Use data-value attribute for reliable matching
                const buttonValue = btn.getAttribute('data-value');
                if (buttonValue === interviewConfig.seniority) {
                    btn.classList.add('selected');
                }
            });
            
            // Show skills section when seniority is selected
            skillsSection.classList.remove('hidden');
        } else {
            experienceSection.classList.remove('selected');
            experienceSection.classList.add('unselected');
            document.querySelectorAll('.experience-btn').forEach(btn => btn.classList.remove('selected'));
            
            // Hide skills section when no seniority is selected
            skillsSection.classList.add('hidden');
        }
    } else {
        experienceSection.classList.add('disabled');
        experienceSection.classList.remove('selected', 'unselected');
        document.querySelectorAll('.experience-btn').forEach(btn => btn.classList.remove('selected'));
        
        // Hide skills section when no role is selected
        skillsSection.classList.add('hidden');
    }
    
    // Update skills section and show relevant skills
    if (interviewConfig.role && interviewConfig.seniority) {
        // Initialize skills array if not already set
        if (!interviewConfig.skills) {
            interviewConfig.skills = [];
        }
        populateSkillsOptions();
        
        // No need to sync checkbox states - using brick selection now
        
        if (interviewConfig.skills && interviewConfig.skills.length === 1) {
            skillsSection.classList.add('selected');
            skillsSection.classList.remove('unselected');
        } else {
            skillsSection.classList.remove('selected');
            skillsSection.classList.add('unselected');
        }
    }
    
    // Enable/disable continue button - require exactly one skill
    if (interviewConfig.role && interviewConfig.seniority && interviewConfig.skills && interviewConfig.skills.length === 1) {
        continueBtn.disabled = false;
        continueBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
        continueBtn.disabled = true;
        continueBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
}

function populateSkillsOptions() {
    const skillsContainer = document.getElementById('skills-options');
    const role = interviewConfig.role;
    const seniority = interviewConfig.seniority;
    
    if (!role || !seniority) {
        skillsContainer.innerHTML = '<p class="text-gray-500 text-center py-4">Please select a role and experience level first.</p>';
        return;
    }

    const skills = getSkillsByRoleAndSeniority(role, seniority);
    
    skillsContainer.innerHTML = skills.map(skill => {
        const isSelected = interviewConfig.skills && interviewConfig.skills.includes(skill);
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

// Handle single skill selection
function handleSkillSelection(selectedSkill) {
    // Clear previous selection
    document.querySelectorAll('.skill-brick').forEach(brick => {
        brick.classList.remove('selected');
    });
    
    // Select new skill
    const selectedBrick = document.querySelector(`[data-skill="${selectedSkill}"]`);
    if (selectedBrick) {
        selectedBrick.classList.add('selected');
    }
    
    // Extract skill name and description
    const skillName = selectedSkill.split(' (')[0]; // Get the part before the first parenthesis
    const skillDescription = selectedSkill.includes('(') ? 
        selectedSkill.substring(selectedSkill.indexOf('(') + 1, selectedSkill.lastIndexOf(')')) : 
        '';
    
    // Update config with both skill name and description
    interviewConfig.skills = [selectedSkill]; // Keep full text for display
    interviewConfig.selectedSkillName = skillName; // Clean skill name for API
    interviewConfig.selectedSkillDescription = skillDescription; // Description for context
    
    console.log('🎯 Skill selected:', {
        fullText: selectedSkill,
        skillName: skillName,
        skillDescription: skillDescription
    });
    
    updateOnboardingUI();
}

// Helper function to sync visual state of skill checkboxes
function syncSkillCheckboxStates() {
    if (!interviewConfig.skills) return;
    
    document.querySelectorAll('.skill-checkbox').forEach(checkbox => {
        const label = checkbox.closest('label');
        const isSelected = interviewConfig.skills.includes(checkbox.value);
        
        // Update checkbox checked state
        checkbox.checked = isSelected;
        
        // Update label visual state
        if (isSelected) {
            label.classList.add('bg-blue-50', 'border', 'border-blue-200');
        } else {
            label.classList.remove('bg-blue-50', 'border', 'border-blue-200');
        }
    });
}

// Continue to dashboard
document.getElementById('onboarding-continue-btn').addEventListener('click', () => {
    if (interviewConfig.role && interviewConfig.seniority && interviewConfig.skills && interviewConfig.skills.length === 1) {
        showScreen('dashboard');
        
        // Update dashboard display
        document.getElementById('dashboard-role-company').textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level).`;
        document.getElementById('key-skills-list').innerHTML = interviewConfig.skills.map(skill => {
            const skillName = skill.split(' (')[0];
            const skillDescription = skill.includes('(') ? 
                skill.substring(skill.indexOf('(') + 1, skill.lastIndexOf(')')) : '';
            return `<li><strong>${skillName}</strong>${skillDescription ? ` - ${skillDescription}` : ''}</li>`;
        }).join('');
    }
});

// Make functions globally accessible for onclick attributes
window.handleRoleSelect = handleRoleSelect;
window.handleExperienceSelect = handleExperienceSelect;

// --- Dashboard and Interview Navigation ---
document.getElementById('go-to-interview-prep-btn').addEventListener('click', () => showScreen('interviewPrep'));
document.getElementById('start-interview-btn').addEventListener('click', startInterview);

// --- Core API Interaction Logic ---
// NEW ASYNCHRONOUS FLOW WITH ORCHESTRATOR:
// 1. startInterview() -> calls /api/start-interview -> gets first question
// 2. handleSubmitAnswer() -> calls /api/submit-answer -> gets next question immediately
// 3. Questions are returned directly in API responses
// 4. Repeat steps 2-3 until interview complete
// 5. endInterview() -> calls /api/interviews/{id}/complete -> shows analysis

async function startInterview() {
    showScreen('interview');
    
    // Start the timer
    startTimer();
    
    // Show loading state
    showQuestionLoading("Starting your AI interview...");
    
    // Clear chat window and show welcome message
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = `
        <div class="text-center py-12 text-gray-600">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center">
                <svg class="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8s9 3.582 9 8-9-8-9-8z"></path>
                </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 mb-2">Interview Session Initializing</h3>
            <p class="text-gray-500">Preparing your personalized interview experience...</p>
        </div>
    `;

    try {
        // Start the interview using the new orchestrator system
        const interviewResponse = await startOrchestratorInterview();
        
        if (interviewResponse && interviewResponse.session_id) {
            sessionId = interviewResponse.session_id;
            interviewId = Date.now(); // Generate a simple ID for tracking
            
            console.log('🎯 Interview started with session ID:', sessionId);
            console.log('🎯 Interview response:', interviewResponse);
            
            // Display the opening statement if it exists in the response
            if (interviewResponse.opening_statement) {
                console.log('🤖 Displaying opening statement from API response');
                displayAIMessage(interviewResponse.opening_statement);
                updateQuestionStatus('Opening statement received');
                enableChatInput();
                updateQuestionStatus('Ready for your answer');
            } else {
                console.log('❌ No opening statement received from API');
                updateQuestionStatus('Error: No opening statement received');
                displayErrorMessage('Failed to receive the opening statement. Please try again.');
            }
            
        } else {
            throw new Error('Failed to start interview - no session ID received');
        }

    } catch (error) {
        console.error('❌ Error starting interview:', error);
        displayErrorMessage('Could not start the interview. Please try again.');
        hideQuestionLoading();
    }
}

// Timer functionality
let timerInterval;
let startTime;

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    const elapsed = Date.now() - startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
}

// Loading state management
function showQuestionLoading(message) {
    const statusElement = document.getElementById('question-status');
    const loaderElement = document.getElementById('question-loader');
    
    if (statusElement) statusElement.textContent = message;
    if (loaderElement) loaderElement.classList.remove('hidden');
}

function hideQuestionLoading() {
    const statusElement = document.getElementById('question-status');
    const loaderElement = document.getElementById('question-loader');
    
    if (statusElement) statusElement.textContent = 'Ready';
    if (loaderElement) loaderElement.classList.add('hidden');
}

// --- Legacy Functions (Kept for backward compatibility) ---
// Note: These functions are from the old synchronous flow and are no longer used
// in the new orchestrator-based asynchronous flow. They're kept here in case
// of fallback scenarios but should be removed in future versions.

function displayCurrentQuestion() {
    // LEGACY: This function is no longer used with the new orchestrator flow
                // Questions now come directly from the API responses
    console.log('⚠️ LEGACY: displayCurrentQuestion called - this should not happen with orchestrator flow');
}

async function generateQuestionsWithGemini() {
    // LEGACY: This function is no longer used with the new orchestrator flow
    // The orchestrator now handles question generation dynamically
    console.log('⚠️ LEGACY: generateQuestionsWithGemini called - this should not happen with orchestrator flow');
    throw new Error('Legacy function called - please use orchestrator flow');
}

async function startOrchestratorInterview() {
    const API_BASE_URL = BACKEND_URL;
    
    // Debug logging to see exactly what URLs are being used
    console.log('🔧 Debug: Configuration check in startOrchestratorInterview');
    console.log('🔧 Debug: BACKEND_URL =', BACKEND_URL);
    console.log('🔧 Debug: API_BASE_URL =', API_BASE_URL);
    console.log('🔧 Debug: window.PREPAI_CONFIG =', window.PREPAI_CONFIG);
    console.log('🔧 Debug: Full config object =', window.PREPAI_CONFIG_FULL);
    
    try {
        console.log('🚀 Starting orchestrator interview with config:', interviewConfig);
        console.log('🚀 Using API endpoint:', `${API_BASE_URL}/api/start-interview`);
        
        const response = await fetch(`${API_BASE_URL}/api/start-interview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                role: interviewConfig.role,
                seniority: interviewConfig.seniority,
                skills: interviewConfig.skills,
                skill_context: {
                    skill_name: interviewConfig.selectedSkillName,
                    skill_description: interviewConfig.selectedSkillDescription,
                    full_skill_text: interviewConfig.skills[0]
                }
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Response error text:', errorText);
            throw new Error(`Server responded with ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log('✅ Interview started successfully:', data);
        
        return data;

    } catch (error) {
        console.error('❌ Error starting orchestrator interview:', error);
        console.error('❌ Error details:', {
            message: error.message,
            stack: error.stack,
            BACKEND_URL,
            API_BASE_URL
        });
        throw error;
    }
}



function displayUserMessage(message) {
    // Use the message template from HTML
    const template = document.getElementById('message-template');
    if (template) {
        const messageElement = template.content.cloneNode(true);
        
        // Update the message content
        const contentDiv = messageElement.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.textContent = message;
        }
        
        // Add user styling
        const messageBubble = messageElement.querySelector('.message-bubble');
        if (messageBubble) {
            messageBubble.classList.add('user');
        }
        
        // Add timestamp
        const metaDiv = messageElement.querySelector('.message-meta');
        if (metaDiv) {
            metaDiv.textContent = new Date().toLocaleTimeString();
        }
        
        // Add to chat window
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
    } else {
        // Fallback to old method
        addMessageToChat(message, 'user');
    }
}

// REMOVED: submitAnswerToOrchestrator function has been replaced by handleSubmitAnswer
// which uses the cleaner, more standard approach from the LLM code

async function endInterview() {
    console.log('🚪 Exit button clicked! Starting endInterview function...');
    
    try {
        // Stop the timer
        console.log('⏱️ Stopping timer...');
        stopTimer();
        console.log('✅ Timer stopped successfully');
        
        console.log('📊 Showing analysis screen...');
        showScreen('analysis');

        // Use the live Render backend URL
        const API_BASE_URL = BACKEND_URL; 
        
        console.log('🌐 Using API URL:', API_BASE_URL);
        
        console.log('📤 Sending completion request to backend...');
        const response = await fetch(`${API_BASE_URL}/api/interview/${sessionId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        console.log('📥 Response received:', response.status, response.statusText);

        if (!response.ok) {
            throw new Error(`Analysis request failed: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        console.log('✅ Analysis completed successfully:', result);

        console.log('📋 Interview completed! Showing feedback screen...');
        showScreen('feedback');
        
        // Format the feedback in a user-friendly way
        if (result.data) {
            const data = result.data;
            feedbackOutput.innerHTML = `
                <div class="space-y-6">
                    <div class="text-center">
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">Interview Analysis Complete!</h3>
                        ${data.overall_score ? `<div class="text-4xl font-bold text-blue-600">${data.overall_score}/5</div>` : ''}
                        <p class="text-gray-600 mt-2">${data.questions_evaluated} questions evaluated</p>
                    </div>
                    
                    ${data.overall_summary ? `
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-blue-800 mb-2">Overall Summary</h4>
                            <p class="text-blue-700">${data.overall_summary}</p>
                        </div>
                    ` : ''}
                    
                    ${data.skills_assessed && data.skills_assessed.length > 0 ? `
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-800 mb-3">Skills Assessed</h4>
                            <div class="flex flex-wrap gap-2">
                                ${data.skills_assessed.map(skill => `
                                    <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">${skill}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${data.detailed_evaluations && data.detailed_evaluations.length > 0 ? `
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-800 mb-3">Detailed Question Analysis</h4>
                            <div class="space-y-4">
                                ${data.detailed_evaluations.map((qa, index) => `
                                    <div class="border-l-4 border-blue-200 pl-4">
                                        <div class="font-medium text-gray-800 mb-2">Question ${index + 1}: ${qa.question.substring(0, 100)}${qa.question.length > 100 ? '...' : ''}</div>
                                        ${qa.evaluation && qa.evaluation.scores ? `
                                            <div class="space-y-2">
                                                ${Object.entries(qa.evaluation.scores).map(([skill, scoreData]) => `
                                                    <div class="flex justify-between items-center text-sm">
                                                        <span class="font-medium text-gray-700">${skill}</span>
                                                        <div class="flex items-center gap-2">
                                                            <span class="text-lg font-bold text-blue-600">${scoreData.score}/5</span>
                                                            <span class="text-xs text-gray-500">${scoreData.feedback.substring(0, 80)}${scoreData.feedback.length > 80 ? '...' : ''}</span>
                                                        </div>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        ` : '<div class="text-gray-500 text-sm">Evaluation data not available</div>'}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="text-center pt-4">
                        <button onclick="location.reload()" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-300">
                            Start a New Interview
                        </button>
                    </div>
                </div>
            `;
        } else {
            console.warn('⚠️ No data in result:', result);
            feedbackOutput.innerHTML = `
                <div class="text-center">
                    <h3 class="text-2xl font-bold text-gray-900 mb-4">Interview Completed</h3>
                    <p class="text-gray-600 mb-6">Your interview has been completed successfully.</p>
                    <button onclick="location.reload()" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-300">
                        Start a New Interview
                    </button>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('❌ Error in endInterview:', error);
        
        // Show error message to user
        feedbackOutput.innerHTML = `
            <div class="text-center">
                <h3 class="text-2xl font-bold text-red-600 mb-4">Error Completing Interview</h3>
                <p class="text-gray-600 mb-6">There was an error completing your interview: ${error.message}</p>
                <button onclick="location.reload()" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-300">
                    Start a New Interview
                </button>
            </div>
        `;
        
        showScreen('feedback');
    }
}

// --- Event Listeners ---
// Event listeners are now set up in setupEventListeners() after DOM loads

// Clean, focused answer submission handler (best of both worlds)
async function handleSubmitAnswer() {
    if (!chatInput) {
        console.error('❌ Chat input not available');
        return;
    }
    
    const answerText = chatInput.value.trim();
    if (!answerText) return; // Don't send empty answers

    console.log('🚀 Submitting answer via orchestrator');

    // 1. Immediately display the user's answer in the chat (like LLM code)
    addMessageToChat(answerText, 'user');
    chatInput.value = ''; // Clear the input field
    
    // 2. Update transcript
    transcript.push({
        question: transcript.length > 0 ? transcript[transcript.length - 1].question : 'First question',
        answer: answerText,
        timestamp: new Date().toISOString()
    });

    // 3. Show loading indicator and disable input (like LLM code + visual feedback)
    showInputLoadingState('processing');
    updateQuestionStatus('Processing your answer...');
    if (chatInput) chatInput.disabled = true;
    if (sendBtn) sendBtn.disabled = true;

    // 4. Send the answer to the backend via HTTP POST (clean approach)
    try {
        const submitUrl = `${BACKEND_URL}/api/submit-answer`;
        console.log('🚀 Submitting answer to:', submitUrl);
        console.log('🚀 Submit data:', { session_id: sessionId, answer: answerText });
        
        const response = await fetch(submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                answer: answerText,
            }),
        });

        console.log('📨 Submit response status:', response.status);
        console.log('📨 Submit response headers:', response.headers);
        
        if (response.ok) {
            // Success - get the next question immediately
            const responseData = await response.json();
            console.log('✅ Answer submitted successfully:', responseData);
            
            if (responseData.success && responseData.next_question) {
                console.log('🎉 Next question received immediately!');
                
                // Hide loading states
                hideInputLoadingStates();
                
                // Handle the AI question
                handleAIQuestion(responseData.next_question);
                
            } else {
                console.error('❌ No next question in response:', responseData);
                addMessageToChat("Error: Could not get next question.", 'system');
                enableChatInput();
            }
        } else {
            // Handle error
            const errorText = await response.text();
            console.error("Failed to submit answer. Status:", response.status, "Response:", errorText);
            addMessageToChat("Error: Could not submit answer.", 'system');
            // Re-enable input on error
            if (chatInput) chatInput.disabled = false;
            if (sendBtn) sendBtn.disabled = false;
            hideInputLoadingStates();
        }

    } catch (error) {
        console.error("Error submitting answer:", error);
        addMessageToChat("Error: Network issue. Please try again.", 'system');
        // Re-enable input on error
        if (chatInput) chatInput.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        hideInputLoadingStates();
        updateQuestionStatus('Ready for your answer');
    }
}



// Handle page refresh/restart
function restart() {
    stopTimer();
    location.reload();
}

// Make restart function globally accessible
window.restart = restart;

// --- Comprehensive Skills Mapping by Role and Seniority ---
function getSkillsByRoleAndSeniority(role, seniority) {
    const skillsMapping = {
        'Product Manager': {
            'Student/Intern': [
                'Basic Product Sense (Understanding what makes a good product)',
                'User Research Fundamentals (Surveys, basic interviews)',
                'Data Analysis Basics (Simple metrics, Excel)',
                'Communication Skills (Clear written and verbal communication)',
                'Basic Project Management (Task organization, timelines)'
            ],
            'Junior / Mid-Level': [
                'Product Sense (Feature prioritization, user value)',
                'User Research (Interviews, usability testing, personas)',
                'Data Analysis (A/B testing, key metrics, dashboards)',
                'Strategic Thinking (Roadmap planning, OKRs)',
                'Execution (Agile processes, stakeholder coordination)',
                'Stakeholder Management (Cross-functional collaboration)',
                'Metrics & KPIs (Defining success metrics)',
                'User Experience Design (Basic UX principles)'
            ],
            'Senior': [
                'Advanced Product Sense (Market positioning, competitive analysis)',
                'Strategic User Research (Market research, user segmentation)',
                'Advanced Data Analysis (Predictive analytics, business intelligence)',
                'Strategic Thinking (Business strategy, market expansion)',
                'Complex Execution (Multi-team coordination, risk management)',
                'Advanced Stakeholder Management (C-level communication, board presentations)',
                'Advanced Metrics & KPIs (Attribution modeling, LTV analysis)',
                'UX Strategy (Design systems, user journey optimization)'
            ],
            'Manager / Lead': [
                'Product Strategy (Portfolio management, market entry)',
                'Research Leadership (Research methodology, team management)',
                'Business Intelligence (Advanced analytics, predictive modeling)',
                'Strategic Leadership (Company vision, market strategy)',
                'Program Management (Multiple product lines, resource allocation)',
                'Executive Stakeholder Management (Board relations, investor communication)',
                'Business Metrics (Financial modeling, market analysis)',
                'Design Leadership (Design strategy, brand management)'
            ]
        },
        'Software Engineer': {
            'Student/Intern': [
                'Basic Coding (Syntax, simple algorithms)',
                'Version Control (Git basics, commit workflow)',
                'Simple Debugging (Error identification, basic fixes)',
                'Basic Testing (Unit test concepts, manual testing)',
                'Documentation (Code comments, README files)'
            ],
            'Junior / Mid-Level': [
                'System Design (Basic architecture patterns)',
                'Algorithms & Data Structures (Common algorithms, optimization)',
                'Code Quality (Clean code, design patterns)',
                'Testing & Debugging (Unit tests, debugging tools)',
                'Performance Optimization (Basic profiling, bottlenecks)',
                'Security (Input validation, authentication)',
                'API Design (REST principles, basic design)',
                'Database Design (Normalization, basic queries)'
            ],
            'Senior': [
                'Advanced System Design (Distributed systems, scalability)',
                'Advanced Algorithms (Complex problem solving, optimization)',
                'Code Quality Leadership (Code reviews, standards)',
                'Testing Strategy (Test automation, CI/CD)',
                'Advanced Performance (Distributed performance, caching)',
                'Security Architecture (Threat modeling, secure design)',
                'API Architecture (Microservices, event-driven)',
                'Database Architecture (Sharding, replication, NoSQL)'
            ],
            'Manager / Lead': [
                'System Architecture (Enterprise architecture, cloud strategy)',
                'Technical Strategy (Technology roadmap, vendor selection)',
                'Quality Engineering (Quality processes, metrics)',
                'DevOps Strategy (Infrastructure as code, monitoring)',
                'Performance Engineering (Capacity planning, optimization)',
                'Security Strategy (Compliance, risk management)',
                'Platform Architecture (Internal platforms, developer experience)',
                'Data Architecture (Data lakes, real-time processing)'
            ]
        },
        'Data Analyst': {
            'Student/Intern': [
                'Basic Excel (Formulas, pivot tables, charts)',
                'Simple Data Visualization (Charts, graphs, basic dashboards)',
                'Basic Statistics (Mean, median, standard deviation)',
                'SQL Fundamentals (SELECT, WHERE, JOIN basics)',
                'Data Cleaning Basics (Handling missing values, duplicates)'
            ],
            'Junior / Mid-Level': [
                'Data Visualization (Tableau, Power BI, advanced charts)',
                'Statistical Analysis (Hypothesis testing, regression)',
                'SQL & Data Querying (Complex queries, optimization)',
                'Business Intelligence (Dashboards, KPI tracking)',
                'A/B Testing (Experiment design, analysis)',
                'Data Storytelling (Narrative building, insights)',
                'Machine Learning Basics (Supervised learning, model evaluation)',
                'Data Quality & Governance (Data validation, documentation)'
            ],
            'Senior': [
                'Advanced Data Visualization (Interactive dashboards, custom charts)',
                'Advanced Statistics (Multivariate analysis, time series)',
                'Advanced SQL (Stored procedures, performance tuning)',
                'Advanced BI (Predictive analytics, real-time dashboards)',
                'Advanced A/B Testing (Multivariate testing, Bayesian analysis)',
                'Advanced Data Storytelling (Executive presentations, strategic insights)',
                'Machine Learning (Unsupervised learning, feature engineering)',
                'Data Strategy (Data architecture, governance frameworks)'
            ],
            'Manager / Lead': [
                'Data Strategy (Data roadmap, platform selection)',
                'Advanced Analytics Leadership (Team management, methodology)',
                'Data Engineering (ETL pipelines, data infrastructure)',
                'Business Intelligence Strategy (Analytics roadmap, tool selection)',
                'Experimentation Strategy (Testing frameworks, cultural change)',
                'Data Communication (Stakeholder management, executive reporting)',
                'AI/ML Strategy (Model deployment, ethical AI)',
                'Data Governance (Compliance, data privacy, quality standards)'
            ]
        }
    };
    
    return skillsMapping[role]?.[seniority] || [];
}

// --- Back Button Functionality ---
function addBackButton(screenElement, targetScreen) {
    // Remove existing back button if any
    const existingBackBtn = screenElement.querySelector('.back-btn');
    if (existingBackBtn) {
        existingBackBtn.remove();
    }
    
    // Create back button with CSS-based positioning
    const backBtn = document.createElement('button');
    backBtn.className = 'back-btn flex items-center gap-2';
    backBtn.innerHTML = `
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        <span class="hidden sm:inline">Back</span>
    `;
    
    backBtn.addEventListener('click', () => {
        console.log('🔙 Back button clicked, navigating to:', targetScreen);
        showScreen(targetScreen);
    });
    
    // Add to screen
    screenElement.appendChild(backBtn);
    
    // Debug logging
    console.log('✅ Back button added to screen:', screenElement.id);
    console.log('✅ Back button classes:', backBtn.className);
    console.log('✅ Back button target screen:', targetScreen);
}

// Function to clean up back button event listeners
function cleanupBackButton(screenElement) {
    const backBtn = screenElement.querySelector('.back-btn');
    if (backBtn) {
        console.log('🧹 Cleaning up back button from screen:', screenElement.id);
        // Remove the button completely
        backBtn.remove();
    } else {
        console.log('ℹ️ No back button found to clean up on screen:', screenElement.id);
    }
}

// --- Initial Load ---
// showScreen('homepage'); // This line is now moved to the DOMContentLoaded listener