// Feedback JavaScript for PrepAI Multi-Page System

// Global variables for feedback state
let interviewTranscript = [];
let interviewConfig = null;
let feedbackData = null;
let radarChart = null;

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
    console.log('📋 Displaying feedback with new structure');
    
    // Store feedback data globally for review modal
    feedbackData = data;
    
    // Hide loading, show feedback
    document.getElementById('loading-screen').classList.add('hidden');
    document.getElementById('feedback-screen').classList.remove('hidden');
    
    // Update role context
    updateRoleContext();
    
    // Update overall score and description
    updateOverallScore(data.overall_score || 3.9);
    
    // Update executive summary
    updateExecutiveSummary(data.overall_feedback);
    
    // Initialize radar chart with skills data
    if (data.scores && Object.keys(data.scores).length > 0) {
        initializeRadarChart(data.scores);
    }
    
    // Generate feedback sections
    generateFeedbackSections(data);
}

// Update role context
function updateRoleContext() {
    if (interviewConfig) {
        const roleContextElement = document.getElementById('role-context');
        if (roleContextElement) {
            const role = interviewConfig.role || 'Software Engineer';
            const seniority = interviewConfig.seniority || 'Mid-Level';
            const skill = interviewConfig.skill || 'General';
            const date = new Date().toLocaleDateString('en-US', { 
                day: 'numeric', 
                month: 'long', 
                year: 'numeric' 
            });
            
            roleContextElement.textContent = `${seniority} ${role} Assessment for ${skill} | ${date}`;
        }
    }
}

// Update overall score display
function updateOverallScore(score) {
    const scoreValueElement = document.getElementById('score-value');
    const scoreCircle = document.getElementById('score-circle');
    const scoreLabel = document.getElementById('score-label');
    const scoreDescription = document.getElementById('score-description');
    
    if (scoreValueElement) {
        scoreValueElement.textContent = score;
    }
    
    if (scoreCircle) {
        // Calculate the angle for the conic gradient (280deg = 78% of 360deg)
        const percentage = (score / 5) * 100;
        const angle = (percentage / 100) * 360;
        scoreCircle.style.background = `conic-gradient(#2563eb 0deg ${angle}deg, #e2e8f0 ${angle}deg 360deg)`;
    }
    
    if (scoreLabel) {
        if (score >= 4.5) {
            scoreLabel.textContent = 'Outstanding Performance';
        } else if (score >= 4.0) {
            scoreLabel.textContent = 'Exceeds Expectations';
        } else if (score >= 3.5) {
            scoreLabel.textContent = 'Good Performance';
        } else if (score >= 3.0) {
            scoreLabel.textContent = 'Meets Expectations';
        } else if (score >= 2.5) {
            scoreLabel.textContent = 'Below Expectations';
        } else {
            scoreLabel.textContent = 'Needs Improvement';
        }
    }
    
    if (scoreDescription) {
        scoreDescription.textContent = `${scoreLabel.textContent} (${score}/5) with room for targeted improvement in specific areas.`;
    }
}

// Update executive summary
function updateExecutiveSummary(feedback) {
    const summaryElement = document.getElementById('executive-summary-text');
    if (summaryElement && feedback) {
        summaryElement.textContent = feedback;
    }
}

// Generate feedback sections
function generateFeedbackSections(data) {
    console.log('📊 Generating feedback sections with new structure');
    
    // Update strengths list
    updateStrengthsList(data.strengths || []);
    
    // Update improvements list
    updateImprovementsList(data.improvements || []);
    
    // Update growth plan
    updateGrowthPlan(data.next_steps || []);
}

// Update strengths list
function updateStrengthsList(strengths) {
    const strengthsList = document.getElementById('strengths-list');
    if (!strengthsList) return;
    
    strengthsList.innerHTML = '';
    
    if (strengths.length === 0) {
        strengthsList.innerHTML = '<li class="feedback-item"><span class="feedback-text">No specific strengths identified in this assessment.</span></li>';
        return;
    }
    
    strengths.forEach(strength => {
        const li = document.createElement('li');
        li.className = 'feedback-item';
        li.innerHTML = `
            <span class="feedback-icon">✓</span>
            <span class="feedback-text">${strength}</span>
        `;
        strengthsList.appendChild(li);
    });
}

// Update improvements list
function updateImprovementsList(improvements) {
    const improvementsList = document.getElementById('improvements-list');
    if (!improvementsList) return;
    
    improvementsList.innerHTML = '';
    
    if (improvements.length === 0) {
        improvementsList.innerHTML = '<li class="feedback-item improvement"><span class="feedback-text">No specific areas for improvement identified.</span></li>';
        return;
    }
    
    improvements.forEach(improvement => {
        const li = document.createElement('li');
        li.className = 'feedback-item improvement';
        li.innerHTML = `
            <span class="feedback-icon">!</span>
            <span class="feedback-text">${improvement}</span>
        `;
        improvementsList.appendChild(li);
    });
}

// Update growth plan
function updateGrowthPlan(nextSteps) {
    const growthPlanContent = document.getElementById('growth-plan-content');
    if (!growthPlanContent) return;
    
    if (nextSteps.length === 0) {
        growthPlanContent.innerHTML = `
            <div class="general-next-steps">
                <h4><span class="icon">N</span>Next Steps</h4>
                <ul>
                    <li>Practice similar questions to build confidence</li>
                    <li>Review your answers and identify areas for improvement</li>
                    <li>Consider mock interviews with different scenarios</li>
                </ul>
            </div>
        `;
        return;
    }
    
    const nextStepsHTML = nextSteps.map(step => `<li>${step}</li>`).join('');
    
    growthPlanContent.innerHTML = `
        <div class="general-next-steps">
            <h4><span class="icon">N</span>Your Personalized Growth Plan</h4>
            <ul>
                ${nextStepsHTML}
            </ul>
        </div>
    `;
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
    // Show detailed review modal with AI evaluations and ideal responses
    if (feedbackData && feedbackData.detailed_evaluations) {
        showDetailedReview(feedbackData.detailed_evaluations);
    } else if (interviewTranscript && interviewTranscript.length > 0) {
        // Fallback to basic transcript if no detailed evaluations
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

function showDetailedReview(detailedEvaluations) {
    // Create comprehensive modal with detailed evaluations
    const modalHTML = `
        <div id="review-modal" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-100">
                <div class="sticky top-0 bg-gray-50 border-b border-gray-200 px-8 py-6 rounded-t-3xl">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-3xl font-bold text-gray-900 mb-2">Detailed Answer Review</h2>
                            <p class="text-gray-600 text-lg">Review each question with AI evaluation and ideal response examples</p>
                            ${feedbackData.role && feedbackData.seniority ? 
                                `<div class="mt-2 text-sm text-gray-500">
                                    <span class="font-semibold">Role:</span> ${feedbackData.role} | 
                                    <span class="font-semibold">Level:</span> ${feedbackData.seniority}
                                </div>` : ''
                            }
                        </div>
                        <button onclick="closeDetailedReview()" class="text-gray-400 hover:text-gray-600 text-3xl font-bold w-12 h-12 rounded-full hover:bg-gray-100 flex items-center justify-center transition-all">&times;</button>
                    </div>
                </div>
                
                <div class="p-8 space-y-8">
                    ${detailedEvaluations.map((evalData, index) => {
                        const evaluation = evalData.evaluation;
                        const score = evaluation.overall_score || 0;
                        const scoreColor = score >= 4 ? 'from-green-500 to-emerald-500' : 
                                         score >= 3 ? 'from-blue-500 to-blue-600' : 
                                         score >= 2 ? 'from-yellow-500 to-orange-500' : 'from-red-500 to-pink-500';
                        
                        return `
                            <div class="border border-gray-200 rounded-2xl p-8 bg-gray-50 shadow-lg">
                                <div class="flex items-start justify-between mb-6">
                                    <h3 class="text-xl font-bold text-gray-900">Q${index + 1}: ${evalData.question}</h3>
                                    <div class="bg-gradient-to-r ${scoreColor} text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg">Score: ${score}/5</div>
                                </div>
                                
                                <div class="mb-6">
                                    <h4 class="font-bold text-gray-800 mb-3 text-lg">Your Answer:</h4>
                                    <div class="bg-gray-100 p-6 rounded-xl border border-gray-200 shadow-sm">
                                        <p class="text-gray-800 text-lg leading-relaxed">${evalData.answer}</p>
                                    </div>
                                </div>
                                
                                <div class="mb-6">
                                    <h4 class="font-bold text-gray-800 mb-3 text-lg">AI Evaluation:</h4>
                                    <div class="bg-gray-100 p-6 rounded-xl border border-gray-200">
                                        <p class="text-gray-800 text-lg"><strong>Overall Feedback:</strong> ${evaluation.overall_feedback || 'No feedback available'}</p>
                                        ${evaluation.scores ? Object.entries(evaluation.scores).map(([skill, skillData]) => 
                                            `<p class="text-gray-800 mt-2 text-lg"><strong>${skill}:</strong> ${skillData.score}/5 - ${skillData.feedback}</p>`
                                        ).join('') : ''}
                                    </div>
                                </div>
                                
                                <div>
                                    <h4 class="font-bold text-gray-800 mb-3 text-lg">
                                        Ideal Response Example 
                                        ${feedbackData.role && feedbackData.seniority ? 
                                            `<span class="text-sm font-normal text-gray-600">(for ${feedbackData.seniority} ${feedbackData.role})</span>` : ''
                                        }
                                    </h4>
                                    <div class="bg-gray-100 p-6 rounded-xl border border-gray-200">
                                        <p class="text-gray-800 text-lg leading-relaxed">${evaluation.ideal_response || 'No ideal response available'}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                
                <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-8 py-6 rounded-b-3xl">
                    <div class="flex justify-between items-center">
                        <div class="text-lg text-gray-700">
                            <span class="font-bold">Overall Score:</span> <span class="text-2xl font-bold text-blue-600">${feedbackData.overall_score || 0}/100</span>
                        </div>
                        <button onclick="closeDetailedReview()" class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                            Close Review
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
}

function closeDetailedReview() {
    const modal = document.getElementById('review-modal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
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

// Initialize radar chart
function initializeRadarChart(skillsData) {
    const ctx = document.getElementById('radarChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (radarChart) {
        radarChart.destroy();
    }
    
    const labels = Object.keys(skillsData);
    const scores = Object.values(skillsData).map(skill => skill.score);
    
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Your Skills',
                data: scores,
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        color: '#64748b',
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    },
                    pointLabels: {
                        color: '#1e293b',
                        font: {
                            size: 14,
                            weight: '600'
                        }
                    },
                    grid: {
                        color: '#e2e8f0'
                    },
                    angleLines: {
                        color: '#e2e8f0'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        loadInterviewData,
        generateFeedback,
        displayFeedback,
        handleStartNewInterview,
        handleReviewAnswers,
        showDetailedReview,
        closeDetailedReview,
        initializeRadarChart
    };
}
