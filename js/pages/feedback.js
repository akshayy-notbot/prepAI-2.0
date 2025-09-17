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
        
        console.log('📊 Interview data loaded:');
        console.log('   Transcript items:', interviewTranscript?.length || 0);
        console.log('   Config:', interviewConfig);
        
        // Debug sessionStorage data
        console.log('🔍 Raw sessionStorage data:');
        console.log('   Transcript:', transcriptData?.substring(0, 200) + '...');
        console.log('   Config:', configData);
        
        // Validate loaded data
        if (!interviewTranscript || interviewTranscript.length === 0) {
            console.error('❌ No transcript data found in sessionStorage');
            return;
        }
        
        if (!interviewConfig || !interviewConfig.role || !interviewConfig.seniority) {
            console.error('❌ Invalid or missing config data in sessionStorage');
            console.error('   Expected fields: role, seniority, skills/skill');
            return;
        }
        
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
        
        // Comprehensive debug logging
        console.log('📤 Sending evaluation request:');
        console.log('   Role:', evaluationRequest.role);
        console.log('   Seniority:', evaluationRequest.seniority);
        console.log('   Skills:', evaluationRequest.skills);
        console.log('   Transcript length:', evaluationRequest.transcript?.length || 0);
        
        // Check transcript structure
        if (evaluationRequest.transcript && evaluationRequest.transcript.length > 0) {
            console.log('📋 First transcript item:');
            console.log('   Keys:', Object.keys(evaluationRequest.transcript[0]));
            console.log('   Has question:', !!evaluationRequest.transcript[0].question);
            console.log('   Has answer:', !!evaluationRequest.transcript[0].answer);
            console.log('   Sample:', evaluationRequest.transcript[0]);
        } else {
            console.error('❌ Transcript is empty or invalid!');
        }
        
        // Validate data before sending
        if (!evaluationRequest.role || !evaluationRequest.seniority) {
            console.error('❌ Missing required fields: role or seniority');
        }
        
        if (!evaluationRequest.transcript || evaluationRequest.transcript.length === 0) {
            console.error('❌ Transcript is empty or missing');
        }
        
        // Log the full request for debugging
        console.log('📦 Full request body:', JSON.stringify(evaluationRequest, null, 2));
        
        // TEMPORARY: Test with debug endpoint first
        const USE_DEBUG_ENDPOINT = false; // Set to true for debugging request issues
        
        // Call the enhanced evaluation API
        const API_BASE_URL = window.PREPAI_CONFIG?.API_BASE_URL || 'https://prepai-api.onrender.com';
        
        const endpoint = USE_DEBUG_ENDPOINT ? '/api/debug-request' : '/api/evaluate-interview-enhanced';
        console.log(`🔗 Using endpoint: ${API_BASE_URL}${endpoint}`);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(evaluationRequest)
        });
        
        if (!response.ok) {
            let errorDetails = 'No error details available';
            try {
                const errorText = await response.text();
                console.error('❌ Server error response (raw):', errorText);
                
                // Try to parse as JSON for better error details
                try {
                    const errorJson = JSON.parse(errorText);
                    errorDetails = errorJson.detail || errorText;
                    console.error('❌ Parsed error details:', errorJson);
                } catch (parseError) {
                    errorDetails = errorText;
                    console.error('❌ Raw error text:', errorText);
                }
            } catch (readError) {
                console.error('❌ Could not read error response:', readError);
            }
            
            throw new Error(`Server responded with ${response.status}: ${errorDetails}`);
        }
        
        const data = await response.json();
        console.log('✅ Response received successfully:', data);
        console.log('📊 Response keys:', Object.keys(data));
        if (data.overall_assessment) {
            console.log('📊 Overall assessment keys:', Object.keys(data.overall_assessment));
        }
        
        if (USE_DEBUG_ENDPOINT) {
            console.log('🔍 Debug response - checking what backend received:');
            console.log('   Received data keys:', Object.keys(data.received_data || {}));
            console.log('   Backend saw request as:', data.received_data);
            
            // Don't try to display dashboard with debug data
            console.log('🛑 Debug mode active - check console logs above for request analysis');
            alert('Debug mode: Check console for detailed request analysis');
            return;
        }
        
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
    
    // Update duration display
    updateDurationDisplay();
    
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
    
    // Generate smart action items
    generateActionItems(data);
    
    // Generate enhanced transcript
    generateEnhancedTranscript();
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

// Update duration display
function updateDurationDisplay() {
    const durationElement = document.getElementById('session-duration');
    if (durationElement && interviewConfig) {
        if (interviewConfig.durationFormatted) {
            durationElement.textContent = interviewConfig.durationFormatted;
        } else if (interviewConfig.duration) {
            // Fallback: format duration from seconds
            const minutes = Math.floor(interviewConfig.duration / 60);
            const seconds = interviewConfig.duration % 60;
            durationElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            durationElement.textContent = 'N/A';
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
        scoreValueElement.textContent = `${score}/5`;
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

// Generate smart action items from evaluation data
function generateActionItems(evaluationData) {
    const actionItemsList = document.getElementById('action-items-list');
    if (!actionItemsList) {
        console.error('❌ Action items list not found');
        return;
    }
    
    // Clear existing content
    actionItemsList.innerHTML = '';
    
    // Get smart action items from backend (now pre-generated)
    const actionItems = evaluationData.action_items || [];
    
    if (actionItems.length === 0) {
        actionItemsList.innerHTML = '<p class="text-gray-500">No specific action items identified. Continue practicing to improve your interview skills.</p>';
        return;
    }
    
    console.log(`📋 Displaying ${actionItems.length} smart action items`);
    
    // Generate enhanced action item cards
    actionItems.forEach((item, index) => {
        const actionItemCard = createSmartActionItemCard(item, index);
        actionItemsList.appendChild(actionItemCard);
    });
}

// Create smart action item card with enhanced features
function createSmartActionItemCard(item, index) {
    const card = document.createElement('div');
    card.className = 'smart-action-item-card';
    card.setAttribute('data-priority', item.priority?.toLowerCase() || 'medium');
    card.setAttribute('data-category', item.category?.toLowerCase().replace(/\s+/g, '-') || 'general');
    
    const priorityColor = {
        'Critical': 'text-red-600 bg-red-50 border-red-200',
        'High': 'text-orange-600 bg-orange-50 border-orange-200',
        'Medium': 'text-yellow-600 bg-yellow-50 border-yellow-200',
        'Low': 'text-green-600 bg-green-50 border-green-200'
    }[item.priority] || 'text-gray-600 bg-gray-50 border-gray-200';
    
    const categoryColor = {
        'Technical Skills': 'text-blue-600 bg-blue-50',
        'Communication': 'text-purple-600 bg-purple-50',
        'Leadership': 'text-indigo-600 bg-indigo-50',
        'Problem Solving': 'text-pink-600 bg-pink-50',
        'Domain Knowledge': 'text-teal-600 bg-teal-50',
        'General Development': 'text-gray-600 bg-gray-50'
    }[item.category] || 'text-gray-600 bg-gray-50';
    
    // Create evidence section if available
    const evidenceSection = item.evidence && item.evidence.length > 0 ? `
        <div class="action-item-evidence">
            <button class="evidence-toggle" onclick="toggleEvidence(${index})">
                <span class="evidence-icon">📋</span>
                <span class="evidence-text">Evidence (${item.evidence.length})</span>
                <span class="evidence-arrow">▼</span>
            </button>
            <div class="evidence-content" id="evidence-${index}" style="display: none;">
                <ul class="evidence-list">
                    ${item.evidence.map(quote => `<li class="evidence-quote">"${quote}"</li>`).join('')}
                </ul>
            </div>
        </div>
    ` : '';
    
    // Create resources section if available
    const resourcesSection = item.resources && item.resources.length > 0 ? `
        <div class="action-item-resources">
            <h5 class="resources-title">Resources:</h5>
            <ul class="resources-list">
                ${item.resources.map(resource => `<li class="resource-item">${resource}</li>`).join('')}
            </ul>
        </div>
    ` : '';
    
    card.innerHTML = `
        <div class="action-item-header">
            <h4 class="action-item-title">${item.title}</h4>
            <div class="action-item-badges">
                <span class="priority-badge ${priorityColor}">${item.priority || 'Medium'}</span>
                <span class="category-badge ${categoryColor}">${item.category || 'General'}</span>
                ${item.timeframe ? `<span class="timeframe-badge">${item.timeframe}</span>` : ''}
            </div>
        </div>
        <div class="action-item-content">
            <p class="action-item-description">${item.description}</p>
            
            ${item.expectedOutcome ? `
                <div class="action-item-outcome">
                    <h5 class="outcome-title">Expected Outcome:</h5>
                    <p class="outcome-text">${item.expectedOutcome}</p>
                </div>
            ` : ''}
            
            ${item.seniorityContext ? `
                <div class="action-item-context">
                    <h5 class="context-title">Why This Matters:</h5>
                    <p class="context-text">${item.seniorityContext}</p>
                </div>
            ` : ''}
            
            ${item.goodVsGreat ? `
                <div class="action-item-improvement">
                    <h5 class="improvement-title">Good vs Great:</h5>
                    <p class="improvement-text">${item.goodVsGreat}</p>
                </div>
            ` : ''}
            
            ${evidenceSection}
            ${resourcesSection}
        </div>
    `;
    
    return card;
}

// Toggle evidence display
function toggleEvidence(index) {
    const evidenceContent = document.getElementById(`evidence-${index}`);
    const evidenceArrow = document.querySelector(`#evidence-${index}`).previousElementSibling.querySelector('.evidence-arrow');
    
    if (evidenceContent.style.display === 'none') {
        evidenceContent.style.display = 'block';
        evidenceArrow.textContent = '▲';
    } else {
        evidenceContent.style.display = 'none';
        evidenceArrow.textContent = '▼';
    }
}

// Legacy function for backward compatibility
function createActionItemCard(item) {
    return createSmartActionItemCard(item, 0);
}

// Generate enhanced transcript with individual analysis
function generateEnhancedTranscript() {
    const transcriptContent = document.getElementById('transcript-content');
    if (!transcriptContent) {
        console.error('❌ Transcript content container not found');
        return;
    }
    
    // Clear existing content
    transcriptContent.innerHTML = '';
    
    if (!interviewTranscript || interviewTranscript.length === 0) {
        transcriptContent.innerHTML = '<p class="text-gray-500">No interview transcript available</p>';
        return;
    }
    
    // Generate Q&A analysis for each transcript item
    interviewTranscript.forEach((item, index) => {
        if (item.question && item.answer) {
            const qaAnalysis = createQAAnalysis(item, index + 1);
            transcriptContent.appendChild(qaAnalysis);
        }
    });
}

// Create individual Q&A analysis card (simplified format)
function createQAAnalysis(item, questionNumber) {
    const qaCard = document.createElement('div');
    qaCard.className = 'qa-simple-card';
    
    const evaluation = item.evaluation || {};
    const overallScore = evaluation.overall_score || 0;
    const idealResponse = evaluation.ideal_response || '';
    const overallFeedback = evaluation.overall_feedback || '';
    
    qaCard.innerHTML = `
        <div class="qa-simple-header">
            <div class="qa-question-text">
                <strong>Q${questionNumber}:</strong> ${item.question}
            </div>
            <div class="qa-score-badge">
                ${overallScore}/5
            </div>
        </div>
        
        <div class="qa-answer-text">
            <strong>Your Answer:</strong> ${item.answer}
        </div>
        
        ${overallFeedback ? `
        <div class="qa-feedback-text">
            <strong>Feedback:</strong> ${overallFeedback}
        </div>
        ` : ''}
        
        ${idealResponse ? `
        <div class="qa-ideal-section">
            <div class="qa-ideal-header">
                <strong>Ideal Answer:</strong>
            </div>
            <div class="qa-ideal-content">
                ${idealResponse}
            </div>
        </div>
        ` : ''}
    `;
    
    return qaCard;
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
                            <h2 class="text-3xl font-bold text-gray-900 mb-2" style="font-family: 'Playfair Display', serif;">Detailed Performance Review</h2>
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
