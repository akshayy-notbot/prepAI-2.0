// --- Global State ---
let interviewId = null;
let sessionId = null;  // Store session ID from backend
let questions = [];
let currentQuestionIndex = 0;
let transcript = [];
let interviewConfig = {}; // To store user selections

let isWaitingForAI = false; // Track if we're waiting for AI response

// --- Screen & Element References ---
const screens = {
    homepage: document.getElementById('homepage-screen'),
    onboarding: document.getElementById('onboarding-screen'), // New: Single onboarding screen
    dashboard: document.getElementById('dashboard-screen'),
    interviewPrep: document.getElementById('interview-prep-screen'),
    interview: document.getElementById('interview-screen'),
    analysis: document.getElementById('analysis-screen'),
    feedback: document.getElementById('feedback-screen'),
};

const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const feedbackOutput = document.getElementById('feedback-output');
const sendBtn = document.getElementById('send-btn');

// --- Helper Functions ---
function showScreen(screenKey) {
    Object.values(screens).forEach(screen => screen.classList.add('hidden'));
    if (screens[screenKey]) {
        screens[screenKey].classList.remove('hidden');
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
    document.addEventListener('DOMContentLoaded', validateConfiguration);
} else {
    validateConfiguration();
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

// Enhanced addMessageToChat function (like your LLM code but with better styling)
function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message flex gap-4 mb-6';
    
    // Avatar and message alignment (like your LLM code)
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
            </div>
        `;
    }
    
    // Message bubble
    const messageBubble = document.createElement('div');
    messageBubble.className = 'flex-grow';
    messageBubble.innerHTML = `
        <div class="message-bubble p-4 rounded-xl ${sender === 'user' ? 'user' : 'ai'}">
            <div class="message-content leading-relaxed">${message}</div>
            <div class="message-meta text-xs text-gray-500 mt-3 font-mono">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(messageBubble);
    
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
                // Remove the error message
                messageElement.remove();
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
    userInput.disabled = false;
    submitButton.disabled = false;
    userInput.focus();
    isWaitingForAI = false;
    
    // Update status
    updateQuestionStatus('Ready for your answer');
}

function disableChatInput() {
    userInput.disabled = true;
    submitButton.disabled = true;
    isWaitingForAI = true;
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
document.getElementById('start-onboarding-btn').addEventListener('click', () => showScreen('onboarding'));

// Role selection handler
function handleRoleSelect(role) {
    interviewConfig.role = role;
    updateOnboardingUI();
}

// Experience selection handler
function handleExperienceSelect(level) {
    interviewConfig.seniority = level;
    updateOnboardingUI();
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
    } else {
        roleSection.classList.remove('selected');
        roleSection.classList.add('unselected');
        document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('selected'));
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
        } else {
            experienceSection.classList.remove('selected');
            experienceSection.classList.add('unselected');
            document.querySelectorAll('.experience-btn').forEach(btn => btn.classList.remove('selected'));
        }
    } else {
        experienceSection.classList.add('disabled');
        experienceSection.classList.remove('selected', 'unselected');
        document.querySelectorAll('.experience-btn').forEach(btn => btn.classList.remove('selected'));
    }
    
    // Update skills section and show relevant skills
    if (interviewConfig.role && interviewConfig.seniority) {
        skillsSection.classList.remove('hidden');
        // Initialize skills array if not already set
        if (!interviewConfig.skills) {
            interviewConfig.skills = [];
        }
        populateSkillsOptions();
        
        // Sync checkbox states after populating
        setTimeout(() => syncSkillCheckboxStates(), 0);
        
        if (interviewConfig.skills && interviewConfig.skills.length > 0) {
            skillsSection.classList.add('selected');
            skillsSection.classList.remove('unselected');
        } else {
            skillsSection.classList.remove('selected');
            skillsSection.classList.add('unselected');
        }
    } else {
        skillsSection.classList.add('hidden');
    }
    
    // Enable/disable continue button
    if (interviewConfig.role && interviewConfig.seniority && interviewConfig.skills && interviewConfig.skills.length > 0) {
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
    
    // Define skills for each role
    const roleSkills = {
        'Product Manager': [
            'Product Sense',
            'User Research',
            'Data Analysis',
            'Strategic Thinking',
            'Execution',
            'Stakeholder Management',
            'Metrics & KPIs',
            'User Experience Design'
        ],
        'Software Engineer': [
            'System Design',
            'Algorithms & Data Structures',
            'Code Quality',
            'Testing & Debugging',
            'Performance Optimization',
            'Security',
            'API Design',
            'Database Design'
        ],
        'Data Analyst': [
            'Data Visualization',
            'Statistical Analysis',
            'SQL & Data Querying',
            'Business Intelligence',
            'A/B Testing',
            'Data Storytelling',
            'Machine Learning Basics',
            'Data Quality & Governance'
        ]
    };
    
    const skills = roleSkills[role] || [];
    
    skillsContainer.innerHTML = skills.map(skill => {
        const isChecked = interviewConfig.skills && interviewConfig.skills.includes(skill);
        const checkedAttr = isChecked ? 'checked' : '';
        const labelClass = isChecked ? 'bg-blue-50 border border-blue-200' : '';
        
        return `
            <label class="flex items-center space-x-3 cursor-pointer p-3 rounded-lg hover:bg-blue-50 transition-colors ${labelClass}">
                <input type="checkbox" value="${skill}" class="skill-checkbox form-checkbox h-5 w-5 text-blue-600 rounded" ${checkedAttr}>
                <span class="text-gray-700">${skill}</span>
            </label>
        `;
    }).join('');
    
    // Add event listeners to all skill checkboxes
    const skillCheckboxes = skillsContainer.querySelectorAll('.skill-checkbox');
    skillCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            handleSkillToggle();
        });
    });
}

// Handle skill selection/deselection
function handleSkillToggle() {
    const selectedSkills = Array.from(document.querySelectorAll('#skills-options input:checked'))
        .map(input => input.value);
    interviewConfig.skills = selectedSkills;
    
    // Add visual feedback for selected skills
    document.querySelectorAll('.skill-checkbox').forEach(checkbox => {
        const label = checkbox.closest('label');
        if (checkbox.checked) {
            label.classList.add('bg-blue-50', 'border', 'border-blue-200');
        } else {
            label.classList.remove('bg-blue-50', 'border', 'border-blue-200');
        }
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
    if (interviewConfig.role && interviewConfig.seniority && interviewConfig.skills && interviewConfig.skills.length > 0) {
        showScreen('dashboard');
        
        // Update dashboard display
        document.getElementById('dashboard-role-company').textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level).`;
        document.getElementById('key-skills-list').innerHTML = interviewConfig.skills.map(skill => `<li>${skill}</li>`).join('');
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
                skills: interviewConfig.skills
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
    // Stop the timer
    stopTimer();
    
    showScreen('analysis');

    // Use the live Render backend URL
    const API_BASE_URL = BACKEND_URL; 
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                transcript: transcript,
                session_id: sessionId,  // Pass session ID for database tracking
                role: interviewConfig.role,  // Pass role for context
                seniority: interviewConfig.seniority,  // Pass seniority for context
                skills: interviewConfig.skills  // Pass skills for context
            })
        });

        if (!response.ok) {
            throw new Error('Analysis request failed');
        }

        const result = await response.json();

        showScreen('feedback');
        
        // Format the feedback in a user-friendly way
        if (result.data) {
            const data = result.data;
            feedbackOutput.innerHTML = `
                <div class="space-y-6">
                    <div class="text-center">
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">Interview Analysis Complete!</h3>
                        ${data.overall_score ? `<div class="text-4xl font-bold text-blue-600">${data.overall_score}/5</div>` : ''}
                    </div>
                    
                    ${data.overall_summary ? `
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-blue-800 mb-2">Overall Summary</h4>
                            <p class="text-blue-700">${data.overall_summary}</p>
                        </div>
                    ` : ''}
                    
                    ${data.scores && data.scores.length > 0 ? `
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-800 mb-3">Detailed Scores</h4>
                            <div class="space-y-3">
                                ${data.scores.map(score => `
                                    <div class="flex justify-between items-start">
                                        <div class="flex-1">
                                            <div class="font-medium text-gray-700">${score.criterion}</div>
                                            <div class="text-sm text-gray-600 mt-1">${score.justification}</div>
                                        </div>
                                        <div class="ml-4 text-2xl font-bold text-blue-600">${score.score}/5</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${data.key_strengths && data.key_strengths.length > 0 ? `
                        <div class="bg-green-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-green-800 mb-2">Key Strengths</h4>
                            <ul class="list-disc list-inside text-green-700 space-y-1">
                                ${data.key_strengths.map(strength => `<li>${strength}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${data.areas_for_improvement && data.areas_for_improvement.length > 0 ? `
                        <div class="bg-yellow-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-yellow-800 mb-2">Areas for Improvement</h4>
                            <ul class="list-disc list-inside text-yellow-700 space-y-1">
                                ${data.areas_for_improvement.map(area => `<li>${area}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${data.recommendations && data.recommendations.length > 0 ? `
                        <div class="bg-purple-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-purple-800 mb-2">Recommendations</h4>
                            <ul class="list-disc list-inside text-purple-700 space-y-1">
                                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
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
            // Fallback to raw JSON if structure is unexpected
            feedbackOutput.innerHTML = `
                <h3 class="text-xl font-semibold">Analysis Complete!</h3>
                <pre class="mt-4 p-4 bg-gray-100 rounded text-sm whitespace-pre-wrap">${JSON.stringify(result, null, 2)}</pre>
            `;
        }

    } catch (error) {
        console.error('❌ Analysis error:', error);
        alert('Could not get analysis. Please try again.');
        showScreen('interview');
    }
}

// --- Event Listeners ---
// Clean event listener setup (like LLM code)
const submitButton = sendBtn; // Use existing reference
const userInput = chatInput; // Use existing reference

submitButton.addEventListener('click', handleSubmitAnswer);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmitAnswer();
    }
});
document.getElementById('end-interview-btn').addEventListener('click', endInterview);

// Clean, focused answer submission handler (best of both worlds)
async function handleSubmitAnswer() {
    const answerText = userInput.value.trim();
    if (!answerText) return; // Don't send empty answers

    console.log('🚀 Submitting answer via orchestrator');

    // 1. Immediately display the user's answer in the chat (like LLM code)
    addMessageToChat(answerText, 'user');
    userInput.value = ''; // Clear the input field
    
    // 2. Update transcript
    transcript.push({
        question: transcript.length > 0 ? transcript[transcript.length - 1].question : 'First question',
        answer: answerText,
        timestamp: new Date().toISOString()
    });

    // 3. Show loading indicator and disable input (like LLM code + visual feedback)
    showInputLoadingState('processing');
    updateQuestionStatus('Processing your answer...');
    userInput.disabled = true;
    submitButton.disabled = true;

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
            userInput.disabled = false;
            submitButton.disabled = false;
            hideInputLoadingStates();
        }

    } catch (error) {
        console.error("Error submitting answer:", error);
        addMessageToChat("Error: Network issue. Please try again.", 'system');
        // Re-enable input on error
        userInput.disabled = false;
        submitButton.disabled = false;
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

// --- Initial Load ---
showScreen('homepage');