// Interview JavaScript for PrepAI Multi-Page System
// This keeps the interview as a single page for optimal UX

// Global variables for interview state
let interviewConfig = null;
let sessionId = null;
let interviewId = null;
let transcript = [];
let currentQuestionIndex = 0;
let isWaitingForAI = false;
let timerInterval = null;
let startTime = null;

// Initialize interview when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    // Interview page initialized
    
    // Load configuration from multi-page system
    loadInterviewConfiguration();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize interview
    initializeInterview();
});

// Load interview configuration from multi-page system
function loadInterviewConfiguration() {
    // Loading interview configuration
    
    // Try to load from sessionStorage first (from interview-prep page)
    const storedConfig = sessionStorage.getItem('prepai_interview_config');
    if (storedConfig) {
        try {
            interviewConfig = JSON.parse(storedConfig);
            // Configuration loaded from sessionStorage
        } catch (error) {
            console.error('❌ Error parsing stored configuration:', error);
        }
    }
    
    // Fallback: try to load from prepAIState
    if (!interviewConfig && window.prepAIState) {
        interviewConfig = window.prepAIState.interviewConfig;
        // Configuration loaded from prepAIState
    }
    
    // Validate configuration
    if (!interviewConfig || !isValidConfiguration(interviewConfig)) {
        console.error('❌ Invalid or missing configuration');
        showConfigurationError();
        return;
    }
    
    // Display configuration
    displayConfiguration();
}

// Validate interview configuration
function isValidConfiguration(config) {
    return config && 
           config.role && 
           config.seniority && 
           config.skills && 
           config.skills.length > 0;
}

// Show configuration error and redirect
function showConfigurationError() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = `
        <div class="text-center py-12">
            <div class="w-20 h-20 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
                <svg class="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <h3 class="text-xl font-semibold text-red-800 mb-2">Configuration Error</h3>
            <p class="text-red-600 mb-4">Your interview configuration is incomplete or invalid.</p>
            <button onclick="window.location.href='onboarding.html'" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                Go to Onboarding
            </button>
        </div>
    `;
}

// Display configuration in the header
function displayConfiguration() {
    const configDisplay = document.getElementById('interview-config-display');
    if (configDisplay && interviewConfig) {
        configDisplay.textContent = `${interviewConfig.role} (${interviewConfig.seniority}) - ${interviewConfig.skills[0].split(' (')[0]}`;
    }
}

// Setup all event listeners for the interview page
function setupEventListeners() {
    // Send button
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', handleSendMessage);
    }
    
    // Chat input
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', handleKeyPress);
        chatInput.addEventListener('input', handleInputChange);
    }
    
    // Exit button
    const exitButton = document.getElementById('exit-interview-btn');
    if (exitButton) {
        exitButton.addEventListener('click', handleExitInterview);
    }
    
            // Interview event listeners setup complete
}

// Initialize the interview
async function initializeInterview() {
    if (!interviewConfig) {
        console.error('❌ Cannot initialize interview without configuration');
        return;
    }
    
    // Initializing interview with config
    
    // Start timer
    startTimer();
    
    // Show welcome message
    showWelcomeMessage();
    
    // Start the interview
    await startInterview();
}

// Show welcome message
function showWelcomeMessage() {
    const chatMessages = document.getElementById('chat-messages');
    const welcomeMessage = `
        <div class="message ai">
            <div class="message-bubble">
                <p>Welcome to your AI interview! I'm here to help you practice for your ${interviewConfig.role} role at the ${interviewConfig.seniority} level.</p>
                <p class="mt-2">We'll be focusing on: <strong>${interviewConfig.skills[0].split(' (')[0]}</strong></p>
                <p class="mt-2">Take your time with your answers. This is a practice session, so feel free to think through your responses carefully.</p>
                <p class="mt-2">Ready to begin? I'll start with your first question.</p>
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    chatMessages.innerHTML = welcomeMessage;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Start the interview
async function startInterview() {
    try {
        // Starting interview via API
        
        // Show loading state
        showLoadingState(true);
        updateStatus('Starting interview...');
        
        // Call the backend to start the interview
        const response = await startOrchestratorInterview();
        
        if (response && response.session_id) {
            sessionId = response.session_id;
            interviewId = Date.now();
            
            // Interview started with session ID
            
            // Display opening statement if provided
            if (response.opening_statement) {
                displayAIMessage(response.opening_statement);
                updateStatus('Ready for your answer');
                enableInput();
            } else {
                // Fallback: ask first question manually
                displayAIMessage("Let's start with your first question. Can you tell me about your experience with " + interviewConfig.skills[0].split(' (')[0] + "?");
                updateStatus('Ready for your answer');
                enableInput();
            }
            
        } else {
            throw new Error('Failed to start interview - no session ID received');
        }
        
    } catch (error) {
        console.error('❌ Error starting interview:', error);
        displayErrorMessage('Could not start the interview. Please try again.');
        updateStatus('Error starting interview');
    } finally {
        showLoadingState(false);
    }
}

// Start orchestrator interview (API call)
async function startOrchestratorInterview() {
    const API_BASE_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
    
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
                skill_name: interviewConfig.selectedSkillName || interviewConfig.skills[0].split(' (')[0],
                skill_description: interviewConfig.selectedSkillDescription || '',
                full_skill_text: interviewConfig.skills[0]
            }
        })
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('✅ Interview started successfully:', data);
    
    return data;
}

// Handle send message
async function handleSendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message || isWaitingForAI) return;
    
            // Sending message
    
    // Display user message
    displayUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Disable input and show loading
    disableInput();
    showLoadingState(true);
    updateStatus('AI is analyzing your response...');
    
    // Send to backend
    try {
        await submitAnswer(message);
    } catch (error) {
        console.error('❌ Error submitting answer:', error);
        displayErrorMessage('Failed to submit your answer. Please try again.');
        updateStatus('Error submitting answer');
        enableInput();
    } finally {
        showLoadingState(false);
    }
}

// Submit answer to backend
async function submitAnswer(answer) {
    if (!sessionId) {
        throw new Error('No active session');
    }
    
    const API_BASE_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
    
    const response = await fetch(`${API_BASE_URL}/api/submit-answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            answer: answer,
        }),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
            // Answer submitted successfully
    
    if (data.success && data.next_question) {
        // Display next question
        displayAIMessage(data.next_question);
        updateStatus('Ready for your answer');
        enableInput();
    } else {
        // Interview complete
        handleInterviewCompletion(data);
    }
}

// Display AI message
function displayAIMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const aiMessage = `
        <div class="message ai">
            <div class="message-bubble">
                ${message}
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', aiMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to transcript
    transcript.push({
        question: message,
        answer: null,
        timestamp: new Date().toISOString()
    });
}

// Display user message
function displayUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const userMessage = `
        <div class="message user">
            <div class="message-bubble">
                ${message}
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', userMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to transcript
    if (transcript.length > 0) {
        transcript[transcript.length - 1].answer = message;
    }
}

// Display error message
function displayErrorMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const errorMessage = `
        <div class="message ai">
            <div class="message-bubble" style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); color: #dc2626; border: 1px solid rgba(239, 68, 68, 0.2);">
                <strong>Error:</strong> ${message}
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', errorMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle interview completion
function handleInterviewCompletion(data) {
    // Interview completed
    
    const completionMessage = `
        <div class="message ai">
            <div class="message-bubble" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); color: #166534; border: 1px solid rgba(34, 197, 94, 0.2);">
                <p><strong>Interview Complete!</strong> 🎉</p>
                <p class="mt-2">You've successfully completed your interview practice session. Great job!</p>
                <p class="mt-2">You can now exit the interview or review your responses.</p>
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.insertAdjacentHTML('beforeend', completionMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    updateStatus('Interview complete');
    disableInput();
}

// Handle key press in chat input
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
    }
}

// Handle input change for auto-resize
function handleInputChange(event) {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// Enable chat input
function enableInput() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    if (chatInput) chatInput.disabled = false;
    if (sendButton) sendButton.disabled = false;
    
    isWaitingForAI = false;
    
    if (chatInput) chatInput.focus();
}

// Disable chat input
function disableInput() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    if (chatInput) chatInput.disabled = true;
    if (sendButton) sendButton.disabled = true;
    
    isWaitingForAI = true;
}

// Show/hide loading state
function showLoadingState(show) {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.classList.toggle('hidden', !show);
    }
}

// Update interview status
function updateStatus(status) {
    const statusElement = document.getElementById('interview-status');
    if (statusElement) {
        statusElement.textContent = status;
    }
}

// Timer functions
function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    if (!startTime) return;
    
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
        timerInterval = null;
    }
}

// Handle exit interview
function handleExitInterview() {
    if (confirm('Are you sure you want to exit the interview? Your progress will be saved.')) {
        // User exiting interview
        
        // Stop timer
        stopTimer();
        
        // Save transcript to sessionStorage
        try {
            sessionStorage.setItem('prepai_interview_transcript', JSON.stringify(transcript));
            // Transcript saved to sessionStorage
        } catch (error) {
            console.error('❌ Error saving transcript:', error);
        }
        
        // Navigate back to dashboard
        if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
            window.PrepAIUtils.Navigation.goTo('dashboard');
        } else {
            window.location.href = 'dashboard.html';
        }
    }
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        loadInterviewConfiguration,
        startInterview,
        handleSendMessage,
        handleExitInterview
    };
}
