// Enhanced Performance Dashboard JavaScript for PrepAI Multi-Page System

// Global variables for feedback state
let interviewTranscript = [];
let interviewConfig = null;
let evaluationData = null;
let radarChart = null;

// Initialize feedback page when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Performance Dashboard initialized');
    
    // Check if user can access this page
    if (!validatePageAccess()) {
        return;
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Load interview data and generate evaluation
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
    
    // Retry evaluation button
    const retryBtn = document.getElementById('retry-feedback-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', handleRetryEvaluation);
    }
    
    // Skip evaluation button
    const skipBtn = document.getElementById('skip-feedback-btn');
    if (skipBtn) {
        skipBtn.addEventListener('click', handleSkipEvaluation);
    }
    
    console.log('✅ Dashboard event listeners setup complete');
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
        
        // Generate evaluation
        generateEvaluation();
        
    } catch (error) {
        console.error('❌ Error loading interview data:', error);
        showErrorScreen();
    }
}

// Generate evaluation by calling the enhanced evaluation API
async function generateEvaluation() {
    try {
        console.log('🚀 Generating enhanced evaluation...');
        showLoadingScreen();
        
        // Prepare the evaluation request matching backend expectations
        const evaluationRequest = {
            role: interviewConfig.role,
            seniority: interviewConfig.seniority,
            skills: interviewConfig.skills || [interviewConfig.skill || "General"], // Backend expects skills array
            transcript: interviewTranscript // Backend expects transcript field
        };
        
        // Debug logging
        console.log('📤 Sending evaluation request:', {
            role: evaluationRequest.role,
            seniority: evaluationRequest.seniority,
            skills: evaluationRequest.skills,
            transcriptLength: evaluationRequest.transcript?.length || 0,
            sampleTranscriptItem: evaluationRequest.transcript?.[0] || null
        });
        
        // Call the enhanced evaluation API
        const API_BASE_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
        
        const response = await fetch(`${API_BASE_URL}/api/evaluate-interview-enhanced`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(evaluationRequest)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Server error response:', errorText);
            throw new Error(`Server responded with ${response.status}: ${errorText || response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Enhanced evaluation generated successfully:', data);
        
        evaluationData = data;
        displayDashboard(data);
        
    } catch (error) {
        console.error('❌ Error generating evaluation:', error);
        showErrorScreen();
    }
}

// Display the enhanced performance feedback
function displayDashboard(data) {
    console.log('📊 Displaying enhanced performance feedback');
    console.log('📊 Raw evaluation data:', data);
    
    // Store evaluation data globally for review modal
    evaluationData = data;
    
    // Hide loading, show feedback
    document.getElementById('loading-screen').classList.add('hidden');
    document.getElementById('feedback-screen').classList.remove('hidden');
    
    // Update role context
    updateRoleContext();
    
    // Update overall score and description
    if (data.overall_assessment?.overall_score !== undefined && data.overall_assessment?.overall_score !== null) {
        updateOverallScore(data.overall_assessment.overall_score);
    } else {
        console.error('❌ No overall score received from API');
        showScoreError();
    }
    
    // Update executive summary
    updateExecutiveSummary(data.overall_assessment?.executive_summary);
    
    // Initialize radar chart with dimension data
    if (data.dimension_evaluations && Object.keys(data.dimension_evaluations).length > 0) {
        initializeDimensionRadarChart(data.dimension_evaluations);
    }
    
    // Generate dimension performance cards
    if (data.dimension_evaluations) {
        generateDimensionCards(data.dimension_evaluations);
    }
    
    // Generate seniority insights
    if (data.overall_assessment) {
        generateSeniorityInsights(data.overall_assessment);
    }
    
    // Generate interview quality analysis
    if (data.interview_quality) {
        generateInterviewQualityAnalysis(data.interview_quality);
    }
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
        // Calculate the angle for the conic gradient
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

// Show score calculation error
function showScoreError() {
    const scoreValueElement = document.getElementById('score-value');
    const scoreLabel = document.getElementById('score-label');
    const scoreDescription = document.getElementById('score-description');
    const scoreCircle = document.getElementById('score-circle');
    
    if (scoreValueElement) {
        scoreValueElement.textContent = '?';
        scoreValueElement.style.color = '#ef4444';
    }
    
    if (scoreLabel) {
        scoreLabel.textContent = 'Could not calculate score';
        scoreLabel.style.color = '#ef4444';
    }
    
    if (scoreDescription) {
        scoreDescription.textContent = 'Score calculation failed. Please check the console for debugging information.';
        scoreDescription.style.color = '#ef4444';
    }
    
    if (scoreCircle) {
        scoreCircle.style.background = '#f3f4f6';
    }
}

// Update executive summary
function updateExecutiveSummary(executiveSummary) {
    const summaryElement = document.getElementById('executive-summary-text');
    if (summaryElement && executiveSummary) {
        summaryElement.textContent = executiveSummary;
    } else {
        console.warn('⚠️ No executive summary received');
        if (summaryElement) {
            summaryElement.textContent = 'No executive summary available.';
            summaryElement.style.color = '#ef4444';
        }
    }
}

// Initialize dimension radar chart
function initializeDimensionRadarChart(dimensionEvaluations) {
    const ctx = document.getElementById('radarChart');
    if (!ctx) {
        console.error('❌ Radar chart canvas not found');
        return;
    }
    
    // Extract dimension names and scores
    const dimensions = Object.keys(dimensionEvaluations);
    const scores = dimensions.map(dim => dimensionEvaluations[dim].rating || 0);
    
    // Create radar chart
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: dimensions.map(dim => dim.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())),
            datasets: [{
                label: 'Performance Score',
                data: scores,
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
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
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            family: 'Inter',
                            weight: '500'
                        },
                        color: '#374151'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#2563eb',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.parsed.r}/5`;
                        }
                    }
                }
            }
        }
    });
}

// Generate dimension performance cards
function generateDimensionCards(dimensionEvaluations) {
    const dimensionGrid = document.getElementById('dimension-grid');
    if (!dimensionGrid) {
        console.error('❌ Dimension grid not found');
        return;
    }
    
    dimensionGrid.innerHTML = '';
    
    Object.entries(dimensionEvaluations).forEach(([dimensionName, evaluation]) => {
        const dimensionCard = createDimensionCard(dimensionName, evaluation);
        dimensionGrid.appendChild(dimensionCard);
    });
}

// Create individual dimension card
function createDimensionCard(dimensionName, evaluation) {
    const card = document.createElement('div');
    card.className = 'dimension-card';
    
    const displayName = dimensionName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    const rating = evaluation.rating || 0;
    const confidence = evaluation.confidence || 'Medium';
    const strengths = evaluation.strengths || [];
    const improvements = evaluation.areas_for_improvement || [];
    const evidence = evaluation.evidence || [];
    const assessment = evaluation.assessment || 'No assessment available';
    const seniorityAlignment = evaluation.seniority_alignment || 'No alignment data';
    const goodVsGreat = evaluation.good_vs_great || 'Not specified';
    const goodVsGreatAnalysis = evaluation.good_vs_great_analysis || 'No analysis available';
    
    card.innerHTML = `
        <div class="dimension-header">
            <div class="dimension-name">${displayName}</div>
            <div class="dimension-score">
                <div class="score-badge">${rating}/5</div>
                <div class="confidence-indicator">${confidence}</div>
            </div>
        </div>
        
        <div class="dimension-content">
            <div class="content-section">
                <h4>
                    <span class="icon">📝</span>
                    Assessment
                </h4>
                <p class="content-text">${assessment}</p>
            </div>
            
            <div class="content-section">
                <h4>
                    <span class="icon">🎯</span>
                    Seniority Alignment
                </h4>
                <p class="content-text">${seniorityAlignment}</p>
            </div>
            
            <div class="content-section">
                <h4>
                    <span class="icon">🌟</span>
                    Performance Level
                </h4>
                <p class="content-text"><strong>${goodVsGreat}</strong></p>
                <p class="content-text">${goodVsGreatAnalysis}</p>
            </div>
            
            ${strengths.length > 0 ? `
            <div class="content-section">
                <h4>
                    <span class="icon">✅</span>
                    Strengths
                </h4>
                <ul class="content-list">
                    ${strengths.map(strength => `
                        <li class="content-item">
                            <span class="content-icon">•</span>
                            <span class="content-text">${strength}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
            
            ${improvements.length > 0 ? `
            <div class="content-section">
                <h4>
                    <span class="icon">⚠️</span>
                    Areas for Improvement
                </h4>
                <ul class="content-list">
                    ${improvements.map(improvement => `
                        <li class="content-item improvement">
                            <span class="content-icon">•</span>
                            <span class="content-text">${improvement}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
            
            ${evidence.length > 0 ? `
            <div class="content-section">
                <h4>
                    <span class="icon">💬</span>
                    Key Evidence
                </h4>
                ${evidence.map(quote => `
                    <div class="quote-item">"${quote}"</div>
                `).join('')}
            </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// Generate seniority insights
function generateSeniorityInsights(overallAssessment) {
    const insightsContainer = document.getElementById('seniority-insights');
    const insightGrid = document.getElementById('insight-grid');
    
    if (!insightsContainer || !insightGrid) {
        console.error('❌ Seniority insights container not found');
        return;
    }
    
    // Show the container
    insightsContainer.classList.remove('hidden');
    
    // Clear existing content
    insightGrid.innerHTML = '';
    
    // Add growth trajectory
    if (overallAssessment.growth_trajectory) {
        const growthItem = document.createElement('div');
        growthItem.className = 'insight-item';
        growthItem.innerHTML = `
            <h4>Career Growth Trajectory</h4>
            <p>${overallAssessment.growth_trajectory}</p>
        `;
        insightGrid.appendChild(growthItem);
    }
    
    // Add career development
    if (overallAssessment.career_development) {
        const careerItem = document.createElement('div');
        careerItem.className = 'insight-item';
        careerItem.innerHTML = `
            <h4>Career Development</h4>
            <p>${overallAssessment.career_development}</p>
        `;
        insightGrid.appendChild(careerItem);
    }
    
    // Add next steps
    if (overallAssessment.next_steps) {
        const nextStepsItem = document.createElement('div');
        nextStepsItem.className = 'insight-item';
        nextStepsItem.innerHTML = `
            <h4>Next Steps</h4>
            <p>${overallAssessment.next_steps}</p>
        `;
        insightGrid.appendChild(nextStepsItem);
    }
}

// Generate interview quality analysis
function generateInterviewQualityAnalysis(interviewQuality) {
    const qualityContainer = document.getElementById('interview-quality');
    const qualityGrid = document.getElementById('quality-grid');
    
    if (!qualityContainer || !qualityGrid) {
        console.error('❌ Interview quality container not found');
        return;
    }
    
    // Show the container
    qualityContainer.classList.remove('hidden');
    
    // Clear existing content
    qualityGrid.innerHTML = '';
    
    // Add archetype effectiveness
    if (interviewQuality.archetype_effectiveness) {
        const archetypeItem = document.createElement('div');
        archetypeItem.className = 'quality-item';
        archetypeItem.innerHTML = `
            <h4>Archetype Effectiveness</h4>
            <p>${interviewQuality.archetype_effectiveness}</p>
        `;
        qualityGrid.appendChild(archetypeItem);
    }
    
    // Add evidence coverage
    if (interviewQuality.evidence_coverage) {
        const coverageItem = document.createElement('div');
        coverageItem.className = 'quality-item';
        coverageItem.innerHTML = `
            <h4>Evidence Coverage</h4>
            <p>${interviewQuality.evidence_coverage}</p>
        `;
        qualityGrid.appendChild(coverageItem);
    }
    
    // Add interview flow
    if (interviewQuality.interview_flow) {
        const flowItem = document.createElement('div');
        flowItem.className = 'quality-item';
        flowItem.innerHTML = `
            <h4>Interview Flow</h4>
            <p>${interviewQuality.interview_flow}</p>
        `;
        qualityGrid.appendChild(flowItem);
    }
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
    if (evaluationData && evaluationData.dimension_evaluations) {
        showDetailedReview(evaluationData.dimension_evaluations);
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

function showDetailedReview(dimensionEvaluations) {
    // Create comprehensive modal with detailed evaluations
    const modalHTML = `
        <div id="review-modal" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-100">
                <div class="sticky top-0 bg-gray-50 border-b border-gray-200 px-8 py-6 rounded-t-3xl">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-3xl font-bold text-gray-900 mb-2">Detailed Performance Review</h2>
                            <p class="text-gray-600 text-lg">Review each dimension with AI evaluation and evidence</p>
                        </div>
                        <button onclick="closeReviewModal()" class="text-gray-400 hover:text-gray-600">
                            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="p-8">
                    ${Object.entries(dimensionEvaluations).map(([dimension, evaluation]) => `
                        <div class="mb-8 p-6 bg-gray-50 rounded-2xl">
                            <h3 class="text-2xl font-bold text-gray-900 mb-4">${dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-700 mb-2">Performance Rating</h4>
                                    <div class="flex items-center gap-3">
                                        <span class="text-3xl font-bold text-blue-600">${evaluation.rating || 0}/5</span>
                                        <span class="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm">${evaluation.confidence || 'Medium'} Confidence</span>
                                    </div>
                                </div>
                                <div>
                                    <h4 class="text-lg font-semibold text-gray-700 mb-2">Performance Level</h4>
                                    <span class="text-lg font-semibold text-green-600">${evaluation.good_vs_great || 'Not specified'}</span>
                                </div>
                            </div>
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Assessment</h4>
                                <p class="text-gray-600">${evaluation.assessment || 'No assessment available'}</p>
                            </div>
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Seniority Alignment</h4>
                                <p class="text-gray-600">${evaluation.seniority_alignment || 'No alignment data'}</p>
                            </div>
                            ${evaluation.strengths && evaluation.strengths.length > 0 ? `
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Key Strengths</h4>
                                <ul class="list-disc list-inside text-gray-600 space-y-1">
                                    ${evaluation.strengths.map(strength => `<li>${strength}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            ${evaluation.areas_for_improvement && evaluation.areas_for_improvement.length > 0 ? `
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Areas for Improvement</h4>
                                <ul class="list-disc list-inside text-gray-600 space-y-1">
                                    ${evaluation.areas_for_improvement.map(area => `<li>${area}</li>`).join('')}
                                </ul>
                            </div>
                            ` : ''}
                            ${evaluation.evidence && evaluation.evidence.length > 0 ? `
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Evidence from Interview</h4>
                                <div class="space-y-2">
                                    ${evaluation.evidence.map(quote => `
                                        <div class="p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
                                            <p class="text-gray-700 italic">"${quote}"</p>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                            ${evaluation.good_vs_great_analysis ? `
                            <div class="mt-6">
                                <h4 class="text-lg font-semibold text-gray-700 mb-2">Good vs Great Analysis</h4>
                                <p class="text-gray-600">${evaluation.good_vs_great_analysis}</p>
                            </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeReviewModal() {
    const modal = document.getElementById('review-modal');
    if (modal) {
        modal.remove();
    }
}

function handleRetryEvaluation() {
    // Retry the evaluation
    generateEvaluation();
}

function handleSkipEvaluation() {
    // Navigate back to homepage
    handleBackToHomepage();
}

// Make closeReviewModal globally accessible
window.closeReviewModal = closeReviewModal;
