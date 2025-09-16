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
    
    // Show configuration summary first (don't auto-start interview)
    showConfigurationSummary();
});

// Load interview configuration from multi-page system
function loadInterviewConfiguration() {
    // Loading interview configuration
    
    // Try to load from sessionStorage first (from onboarding page)
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
        configDisplay.textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level) to practice ${interviewConfig.skills[0].split(' (')[0]}`;
    }
}

// Show configuration summary
function showConfigurationSummary() {
    const configSummary = document.getElementById('config-summary');
    const interviewInterface = document.getElementById('interview-interface');
    
    if (configSummary && interviewInterface) {
        configSummary.classList.remove('hidden');
        interviewInterface.classList.add('hidden');
    }
}

// Show interview interface
function showInterviewInterface() {
    const configSummary = document.getElementById('config-summary');
    const interviewInterface = document.getElementById('interview-interface');
    
    if (configSummary && interviewInterface) {
        configSummary.classList.add('hidden');
        interviewInterface.classList.remove('hidden');
        
        // Clear any existing chat messages
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        
        // Initialize the interview status
        updateStatus('Starting interview...');
    }
}

// Setup all event listeners for the interview page
function setupEventListeners() {
    // Configuration buttons
    const editConfigBtn = document.getElementById('edit-config-btn');
    if (editConfigBtn) {
        editConfigBtn.addEventListener('click', handleEditConfiguration);
    }
    
    const beginInterviewBtn = document.getElementById('begin-interview-btn');
    if (beginInterviewBtn) {
        beginInterviewBtn.addEventListener('click', handleBeginInterview);
    }
    
    // Back to homepage button
    const backToHomepageBtn = document.getElementById('back-to-homepage-btn');
    if (backToHomepageBtn) {
        backToHomepageBtn.addEventListener('click', handleBackToHomepage);
    }
    
    // Send button
    const sendButton = document.getElementById('send-message-btn');
    if (sendButton) {
        sendButton.addEventListener('click', handleSendMessage);
    }
    
    // Chat input
    const chatInput = document.getElementById('user-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', handleKeyPress);
        chatInput.addEventListener('input', handleInputChange);
    }
    
    // Exit button
    const exitButton = document.getElementById('exit-interview-btn');
    if (exitButton) {
        exitButton.addEventListener('click', handleExitInterview);
    }
    
    // End session button
    const endSessionButton = document.getElementById('end-session-btn');
    if (endSessionButton) {
        endSessionButton.addEventListener('click', handleExitInterview);
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
    
    // Start the interview directly
    await startInterview();
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
        
        console.log('🔍 Full response from startOrchestratorInterview:', response);
        console.log('🔍 Response type:', typeof response);
        console.log('🔍 Response keys:', response ? Object.keys(response) : 'No response');
        console.log('🔍 Session ID check:', response?.session_id);
        
        if (response && response.session_id) {
            sessionId = response.session_id;
            interviewId = Date.now();
            
            console.log('✅ Interview started with session ID:', sessionId);
            
            // Display opening statement if provided
            if (response.opening_statement) {
                console.log('📝 Displaying opening statement:', response.opening_statement);
                displayAIMessage(response.opening_statement);
                updateStatus('Ready for your answer');
                enableInput();
            } else {
                console.log('⚠️ No opening statement, using fallback question');
                // Fallback: ask first question manually
                displayAIMessage("Let's start with your first question. Can you tell me about your experience with " + interviewConfig.skills[0].split(' (')[0] + "?");
                updateStatus('Ready for your answer');
                enableInput();
            }
            
        } else {
            console.error('❌ Response validation failed:');
            console.error('  - Response exists:', !!response);
            console.error('  - Response content:', response);
            console.error('  - Session ID exists:', !!response?.session_id);
            console.error('  - Session ID value:', response?.session_id);
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
    console.log('🔍 Response data type:', typeof data);
    console.log('🔍 Response data keys:', data ? Object.keys(data) : 'No data');
    console.log('🔍 Session ID in data:', data?.session_id);
    
    // Validate the response structure
    if (!data) {
        throw new Error('Empty response from server');
    }
    
    if (!data.session_id) {
        console.error('❌ Missing session_id in response:', data);
        throw new Error('Server response missing session_id field');
    }
    
    return data;
}

// Handle send message
async function handleSendMessage() {
    const chatInput = document.getElementById('user-input');
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
    
    // Check for AI-driven completion first
    if (data.interview_completed) {
        // AI determined interview should complete
        console.log('🎉 Interview completed by AI assessment');
        console.log('📊 Completion reason:', data.completion_reason);
        console.log('📈 Evidence summary:', data.evidence_summary);
        console.log('🎯 Coverage percentage:', data.coverage_percentage);
        
        // Display final message and handle completion
        displayAIMessage(data.next_question);
        handleInterviewCompletion(data);
    } else if (data.success && data.next_question) {
        // Continue interview - display next question
        displayAIMessage(data.next_question);
        updateStatus('Ready for your answer');
        enableInput();
        
        // Log completion assessment for debugging (if available)
        if (data.completion_assessment) {
            console.log('🔍 Coverage status:', data.completion_assessment.evidence_summary);
            console.log('📊 Should complete:', data.completion_assessment.should_complete);
            if (data.completion_assessment.remaining_gaps && data.completion_assessment.remaining_gaps.length > 0) {
                console.log('⚠️ Remaining gaps:', data.completion_assessment.remaining_gaps);
            }
        }
    } else {
        // Fallback - interview complete (shouldn't happen with new logic)
        console.log('⚠️ Interview completed via fallback logic');
        handleInterviewCompletion(data);
    }
}

// Display AI message using working format
function displayAIMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const aiMessage = `
        <div class="chat-message justify-start">
            <div class="message-bubble ai">
                ${message}
                <div class="text-xs text-gray-500 mt-2 font-mono">${new Date().toLocaleTimeString()}</div>
            </div>
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

// Display user message using working format
function displayUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const userMessage = `
        <div class="chat-message justify-end">
            <div class="message-bubble user">
                ${message}
                <div class="text-xs text-gray-500 mt-2 font-mono">${new Date().toLocaleTimeString()}</div>
            </div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', userMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to transcript
    if (transcript.length > 0) {
        transcript[transcript.length - 1].answer = message;
    }
}

// Display error message using working format
function displayErrorMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const errorMessage = `
        <div class="chat-message justify-start">
            <div class="message-bubble ai" style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;">
                <strong>Error:</strong> ${message}
                <div class="text-xs text-gray-500 mt-2 font-mono">${new Date().toLocaleTimeString()}</div>
            </div>
        </div>
    `;
    
    chatMessages.insertAdjacentHTML('beforeend', errorMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle interview completion
function handleInterviewCompletion(data) {
    // Interview completed
    
    // Build completion details if available
    let completionDetails = '';
    if (data.completion_reason) {
        completionDetails += `<p class="mt-2 text-sm"><strong>Completion Assessment:</strong> ${data.completion_reason}</p>`;
    }
    if (data.evidence_summary) {
        completionDetails += `<p class="mt-1 text-sm"><strong>Coverage Achieved:</strong> ${data.evidence_summary}</p>`;
    }
    if (data.coverage_percentage) {
        completionDetails += `<p class="mt-1 text-sm"><strong>Assessment Coverage:</strong> ${data.coverage_percentage}</p>`;
    }
    
    const completionMessage = `
        <div class="message ai">
            <div class="message-bubble" style="background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;">
                <p><strong>Interview Complete!</strong> 🎉</p>
                <p class="mt-2">You've successfully completed your interview practice session. Great job!</p>
                ${completionDetails}
                <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p class="text-sm text-blue-800 mb-3">Ready to see how you performed? Click below to view your detailed evaluation and feedback.</p>
                    <button 
                        id="view-evaluation-btn"
                        onclick="navigateToEvaluation()"
                        class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                        📊 View Interview Evaluation
                    </button>
                </div>
            </div>
            <div class="message-meta">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.insertAdjacentHTML('beforeend', completionMessage);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    updateStatus('Interview complete - Ready for evaluation');
    disableInput();
    
    // Save transcript and config for feedback analysis
    try {
        sessionStorage.setItem('prepai_interview_transcript', JSON.stringify(transcript));
        sessionStorage.setItem('prepai_interview_config', JSON.stringify(interviewConfig));
        console.log('✅ Interview data saved for evaluation');
    } catch (error) {
        console.error('❌ Error saving interview data:', error);
        alert('Warning: Could not save interview data. Evaluation may not work correctly.');
    }
}

// Navigate to evaluation page when user clicks the button
function navigateToEvaluation() {
    console.log('🎯 User initiated navigation to evaluation');
    
    // Disable the button to prevent double-clicks
    const button = document.getElementById('view-evaluation-btn');
    if (button) {
        button.disabled = true;
        button.textContent = '📊 Loading Evaluation...';
        button.classList.add('opacity-50', 'cursor-not-allowed');
    }
    
    // Update status
    updateStatus('Generating your evaluation...');
    
    // Navigate to feedback page
    setTimeout(() => {
        if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
            window.PrepAIUtils.Navigation.goTo('feedback');
        } else {
            window.location.href = 'feedback.html';
        }
    }, 500); // Brief delay to show button state change
}

// Handle key press in chat input
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
    }
    // Allow Shift+Enter for new lines (default textarea behavior)
}

// Handle input change (simplified for single-line input)
function handleInputChange(event) {
    // No auto-resize needed for single-line input
}

// Enable chat input
function enableInput() {
    const chatInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-message-btn');
    
    if (chatInput) chatInput.disabled = false;
    if (sendButton) sendButton.disabled = false;
    
    isWaitingForAI = false;
    
    if (chatInput) chatInput.focus();
}

// Disable chat input
function disableInput() {
    const chatInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-message-btn');
    
    if (chatInput) {
        chatInput.disabled = true;
        chatInput.placeholder = "Interview completed - no further input needed";
        chatInput.classList.add('opacity-50', 'cursor-not-allowed');
    }
    
    if (sendButton) {
        sendButton.disabled = true;
        sendButton.classList.add('opacity-50', 'cursor-not-allowed');
    }
    
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
    const statusElement = document.getElementById('interview-status-display');
    if (statusElement) {
        statusElement.textContent = status;
    }
    
    // Also update the interview status in the chat header
    const interviewStatusElement = document.getElementById('interview-status');
    if (interviewStatusElement) {
        interviewStatusElement.textContent = status;
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

// Handle edit configuration
function handleEditConfiguration() {
    // Navigate back to onboarding to edit configuration
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('onboarding');
    } else {
        window.location.href = 'onboarding.html';
    }
}

// Handle back to homepage
function handleBackToHomepage() {
    // Navigate back to homepage
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('index');
    } else {
        window.location.href = 'index.html';
    }
}

// Handle begin interview
function handleBeginInterview() {
    // Show interview interface
    showInterviewInterface();
    
    // Initialize and start the interview
    initializeInterview();
}

// Handle exit interview
function handleExitInterview() {
    // User exiting interview - no confirmation needed
    
    // Stop timer
    stopTimer();
    
    // Save transcript to sessionStorage for feedback analysis
    try {
        sessionStorage.setItem('prepai_interview_transcript', JSON.stringify(transcript));
        sessionStorage.setItem('prepai_interview_config', JSON.stringify(interviewConfig));
        // Transcript and config saved for feedback
    } catch (error) {
        console.error('❌ Error saving interview data:', error);
    }
    
    // Navigate to feedback page
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('feedback');
    } else {
        window.location.href = 'feedback.html';
    }
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        loadInterviewConfiguration,
        startInterview,
        handleSendMessage,
        handleExitInterview,
        handleEditConfiguration,
        handleBeginInterview,
        handleBackToHomepage
    };
}
