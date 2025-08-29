// Feedback JavaScript for PrepAI Multi-Page System

// Global variables for feedback state
let interviewTranscript = [];
let interviewConfig = null;
let feedbackData = null;

// Initialize feedback when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 Feedback page initialized');
    
    // Check if user can access this page
    if (!validatePageAccess()) {
        return;
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Load interview data and generate feedback
    loadInterviewData();
});

// Validate if user can access this page
function validatePageAccess() {
    // Check if we have interview data
    const transcript = sessionStorage.getItem('prepai_interview_transcript');
    const config = sessionStorage.getItem('prepai_interview_config');
    
    if (!transcript || !config) {
        console.warn('⚠️ No interview data found, redirecting to homepage');
        // Redirect to homepage if no interview data
        if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
            window.PrepAIUtils.Navigation.goTo('index');
        } else {
            window.location.href = 'index.html';
        }
        return false;
    }
    
    return true;
}

// Setup event listeners
function setupEventListeners() {
    console.log('🔧 Setting up feedback event listeners...');
    
    // Back button
    const backBtn = document.getElementById('back-to-homepage-btn');
    if (backBtn) {
        backBtn.addEventListener('click', handleBackToHomepage);
    }
    
    // Start new interview button
    const startNewBtn = document.getElementById('start-new-interview-btn');
    if (startNewBtn) {
        startNewBtn.addEventListener('click', handleStartNewInterview);
    }
    
    // Review answers button
    const reviewBtn = document.getElementById('review-answers-btn');
    if (reviewBtn) {
        reviewBtn.addEventListener('click', handleReviewAnswers);
    }
    
    // Retry feedback button
    const retryBtn = document.getElementById('retry-feedback-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', handleRetryFeedback);
    }
    
    // Skip feedback button
    const skipBtn = document.getElementById('skip-feedback-btn');
    if (skipBtn) {
        skipBtn.addEventListener('click', handleSkipFeedback);
    }
    
    console.log('✅ Feedback event listeners setup complete');
}

// Load interview data from session storage
function loadInterviewData() {
    try {
        // Load transcript
        const transcriptData = sessionStorage.getItem('prepai_interview_transcript');
        if (transcriptData) {
            interviewTranscript = JSON.parse(transcriptData);
        }
        
        // Load config
        const configData = sessionStorage.getItem('prepai_interview_config');
        if (configData) {
            interviewConfig = JSON.parse(configData);
        }
        
        console.log('📊 Interview data loaded:', {
            transcript: interviewTranscript.length + ' interactions',
            config: interviewConfig
        });
        
        // Generate feedback
        generateFeedback();
        
    } catch (error) {
        console.error('❌ Error loading interview data:', error);
        showErrorScreen();
    }
}

// Generate feedback by calling the evaluation API
async function generateFeedback() {
    try {
        console.log('🚀 Generating feedback...');
        showLoadingScreen();
        
        // Prepare the evaluation request
        const evaluationRequest = {
            role: interviewConfig.role,
            seniority: interviewConfig.seniority,
            skills: interviewConfig.skills,
            transcript: interviewTranscript
        };
        
        // Call the evaluation API
        const API_BASE_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
        
        const response = await fetch(`${API_BASE_URL}/api/evaluate-interview`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(evaluationRequest)
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Feedback generated successfully:', data);
        
        feedbackData = data;
        displayFeedback(data);
        
    } catch (error) {
        console.error('❌ Error generating feedback:', error);
        showErrorScreen();
    }
}

// Display feedback data
function displayFeedback(data) {
    console.log('📋 Displaying feedback');
    
    // Hide loading, show feedback
    document.getElementById('loading-screen').classList.add('hidden');
    document.getElementById('feedback-screen').classList.remove('hidden');
    
    // Update overall score
    updateOverallScore(data.overall_score || 75);
    
    // Update overall summary
    const summaryElement = document.getElementById('overall-summary');
    if (summaryElement && data.overall_feedback) {
        summaryElement.textContent = data.overall_feedback;
    }
    
    // Generate feedback sections
    generateFeedbackSections(data);
}

// Update overall score display
function updateOverallScore(score) {
    const scoreElement = document.getElementById('score-text');
    const scoreContainer = document.getElementById('overall-score');
    
    if (scoreElement) {
        scoreElement.textContent = score;
    }
    
    if (scoreContainer) {
        // Remove existing score classes
        scoreContainer.classList.remove('score-excellent', 'score-good', 'score-fair', 'score-poor');
        
        // Add appropriate score class
        if (score >= 90) {
            scoreContainer.classList.add('score-excellent');
        } else if (score >= 75) {
            scoreContainer.classList.add('score-good');
        } else if (score >= 60) {
            scoreContainer.classList.add('score-fair');
        } else {
            scoreContainer.classList.add('score-poor');
        }
    }
}

// Generate feedback sections
function generateFeedbackSections(data) {
    const feedbackContainer = document.getElementById('feedback-content');
    if (!feedbackContainer) return;
    
    feedbackContainer.innerHTML = '';
    
    // Strengths section
    if (data.strengths && data.strengths.length > 0) {
        const strengthsSection = createFeedbackSection('Strengths', data.strengths, 'strength');
        feedbackContainer.appendChild(strengthsSection);
    }
    
    // Areas for improvement
    if (data.improvements && data.improvements.length > 0) {
        const improvementsSection = createFeedbackSection('Areas for Improvement', data.improvements, 'improvement');
        feedbackContainer.appendChild(improvementsSection);
    }
    
    // Specific feedback by category
    if (data.category_feedback) {
        for (const [category, feedback] of Object.entries(data.category_feedback)) {
            const categorySection = createFeedbackSection(
                category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                [feedback],
                'overall'
            );
            feedbackContainer.appendChild(categorySection);
        }
    }
    
    // Overall recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        const recommendationsSection = createFeedbackSection('Recommendations', data.recommendations, 'overall');
        feedbackContainer.appendChild(recommendationsSection);
    }
}

// Create a feedback section
function createFeedbackSection(title, items, type) {
    const section = document.createElement('div');
    section.className = `feedback-section ${type}`;
    
    const titleElement = document.createElement('h3');
    titleElement.className = 'text-lg font-semibold mb-3';
    titleElement.textContent = title;
    
    // Set title color based on type
    if (type === 'strength') {
        titleElement.classList.add('text-green-800');
    } else if (type === 'improvement') {
        titleElement.classList.add('text-yellow-800');
    } else {
        titleElement.classList.add('text-blue-800');
    }
    
    section.appendChild(titleElement);
    
    // Add items
    if (Array.isArray(items)) {
        const list = document.createElement('ul');
        list.className = 'space-y-2';
        
        items.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'flex items-start space-x-2';
            
            const bullet = document.createElement('span');
            bullet.className = 'text-lg mt-0.5';
            
            if (type === 'strength') {
                bullet.textContent = '✅';
                bullet.classList.add('text-green-600');
            } else if (type === 'improvement') {
                bullet.textContent = '💡';
                bullet.classList.add('text-yellow-600');
            } else {
                bullet.textContent = '📌';
                bullet.classList.add('text-blue-600');
            }
            
            const text = document.createElement('span');
            text.className = 'text-gray-700 leading-relaxed';
            text.textContent = item;
            
            listItem.appendChild(bullet);
            listItem.appendChild(text);
            list.appendChild(listItem);
        });
        
        section.appendChild(list);
    } else {
        // Single item (string)
        const text = document.createElement('p');
        text.className = 'text-gray-700 leading-relaxed';
        text.textContent = items;
        section.appendChild(text);
    }
    
    return section;
}

// Show loading screen
function showLoadingScreen() {
    document.getElementById('loading-screen').classList.remove('hidden');
    document.getElementById('feedback-screen').classList.add('hidden');
    document.getElementById('error-screen').classList.add('hidden');
}

// Show error screen
function showErrorScreen() {
    document.getElementById('loading-screen').classList.add('hidden');
    document.getElementById('feedback-screen').classList.add('hidden');
    document.getElementById('error-screen').classList.remove('hidden');
}

// Event handlers
function handleBackToHomepage() {
    // Navigate back to homepage
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('index');
    } else {
        window.location.href = 'index.html';
    }
}

function handleStartNewInterview() {
    // Clear previous interview data
    sessionStorage.removeItem('prepai_interview_transcript');
    sessionStorage.removeItem('prepai_interview_config');
    
    // Navigate to onboarding for new interview
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('onboarding');
    } else {
        window.location.href = 'onboarding.html';
    }
}

function handleReviewAnswers() {
    // Show a modal or navigate to a review page
    // For now, we'll show an alert with the transcript
    if (interviewTranscript && interviewTranscript.length > 0) {
        let reviewText = "Your Interview Responses:\n\n";
        interviewTranscript.forEach((item, index) => {
            if (item.question) {
                reviewText += `Q${index + 1}: ${item.question}\n`;
            }
            if (item.answer) {
                reviewText += `A${index + 1}: ${item.answer}\n\n`;
            }
        });
        alert(reviewText);
    } else {
        alert('No interview responses found to review.');
    }
}

function handleRetryFeedback() {
    // Retry generating feedback
    generateFeedback();
}

function handleSkipFeedback() {
    // Skip feedback and go to homepage
    if (window.PrepAIUtils && window.PrepAIUtils.Navigation) {
        window.PrepAIUtils.Navigation.goTo('index');
    } else {
        window.location.href = 'index.html';
    }
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        loadInterviewData,
        generateFeedback,
        displayFeedback,
        handleStartNewInterview,
        handleReviewAnswers
    };
}
