// Shared Utilities for PrepAI Multi-Page System

// Navigation utilities
const Navigation = {
    // Navigate to a specific page
    goTo(page, params = {}) {
        const baseUrl = window.location.origin + window.location.pathname.replace(/\/[^\/]*$/, '');
        let url = `${baseUrl}/${page}.html`;
        
        // Add query parameters if provided
        if (Object.keys(params).length > 0) {
            const searchParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    searchParams.append(key, value);
                }
            });
            url += `?${searchParams.toString()}`;
        }
        
        console.log(`🚀 Navigating to: ${url}`);
        window.location.href = url;
    },

    // Go back to previous page
    goBack() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            this.goTo('index');
        }
    },

    // Check if current page is valid
    validateCurrentPage() {
        const currentPage = this.getCurrentPage();
        const stateSummary = window.prepAIState?.getStateSummary();
        
        if (!stateSummary) return true; // No state validation needed
        
        // Check if user can access current page
        if (!window.prepAIState.canProceedTo(currentPage)) {
            console.warn(`⚠️ User cannot access ${currentPage}, redirecting to appropriate page`);
            this.redirectToAppropriatePage();
            return false;
        }
        
        return true;
    },

    // Get current page name
    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        return filename.replace('.html', '') || 'index';
    },

    // Redirect to appropriate page based on state
    redirectToAppropriatePage() {
        const stateSummary = window.prepAIState.getStateSummary();
        
        if (!stateSummary.hasRole) {
            this.goTo('onboarding');
        } else if (!stateSummary.hasSeniority) {
            this.goTo('onboarding');
        } else if (!stateSummary.hasSkills) {
            this.goTo('onboarding');
        } else if (!stateSummary.sessionActive) {
            this.goTo('dashboard');
        } else {
            this.goTo('index');
        }
    }
};

// Validation utilities
const Validation = {
    // Validate interview configuration
    validateInterviewConfig(config) {
        const errors = [];
        
        if (!config.role) {
            errors.push('Role is required');
        }
        
        if (!config.seniority) {
            errors.push('Experience level is required');
        }
        
        if (!config.skills || config.skills.length === 0) {
            errors.push('At least one skill must be selected');
        }
        
        if (config.skills && config.skills.length > 1) {
            errors.push('Only one skill can be selected');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    // Validate session data
    validateSession(sessionId, interviewId) {
        return {
            isValid: !!(sessionId && interviewId),
            errors: []
        };
    }
};

// UI utilities
const UI = {
    // Show loading state
    showLoading(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="flex items-center justify-center space-x-3 text-gray-600">
                    <div class="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span class="font-medium">${message}</span>
                </div>
            `;
        }
    },

    // Hide loading state
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    },

    // Show error message
    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    <div class="flex items-center space-x-2">
                        <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span class="font-medium">${message}</span>
                    </div>
                </div>
            `;
        }
    },

    // Show success message
    showSuccess(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                    <div class="flex items-center space-x-2">
                        <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <span class="font-medium">${message}</span>
                    </div>
                </div>
            `;
        }
    },

    // Create back button
    createBackButton(targetPage, container) {
        const backBtn = document.createElement('button');
        backBtn.className = 'back-btn flex items-center gap-2';
        backBtn.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            <span class="hidden sm:inline">Back</span>
        `;
        
        backBtn.addEventListener('click', () => {
            Navigation.goTo(targetPage);
        });
        
        if (container) {
            container.appendChild(backBtn);
        }
        
        return backBtn;
    }
};

// Skills mapping utility (moved from app.js)
const SkillsMapping = {
    getSkillsByRoleAndSeniority(role, seniority) {
        const skillsMapping = {
            'Product Manager': {
                'Junior': [
                    'Product Sense',
                    'Execution',
                    'Communication'
                ],
                'Mid': [
                    'Product Sense',
                    'Execution',
                    'Strategic Thinking',
                    'Leadership & Influence'
                ],
                'Senior': [
                    'Product Sense',
                    'Execution',
                    'Strategic Thinking',
                    'Leadership & Influence'
                ],
                'Manager': [
                    'Product Sense',
                    'Execution',
                    'Strategic Thinking',
                    'Leadership & Influence'
                ]
            },
            'Software Engineer': {
                'Junior': [
                    'Coding Fundamentals',
                    'Understanding Systems',
                    'Team Collaboration'
                ],
                'Mid': [
                    'CS Fundamentals in Practice',
                    'Component-Level Design',
                    'Operational Health'
                ],
                'Senior': [
                    'System Design',
                    'Technical Leadership',
                    'Strategic Implementation'
                ],
                'Manager': [
                    'System Architecture',
                    'Technical Strategy',
                    'Engineering Excellence'
                ]
            },
            'Data Analyst': {
                'Junior': [
                    'Technical Foundations',
                    'Analytical Basics',
                    'Reporting'
                ],
                'Mid': [
                    'Technical Proficiency',
                    'Statistical Analysis',
                    'Business Impact'
                ],
                'Senior': [
                    'Technical Depth',
                    'Advanced Analytics',
                    'Strategic Partnership'
                ],
                'Manager': [
                    'Technical & Systems Thinking',
                    'Strategic Leadership',
                    'Executive Communication & Influence'
                ]
            }
        };
        
        return skillsMapping[role]?.[seniority] || [];
    }
};

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Navigation, Validation, UI, SkillsMapping };
} else {
    // Browser environment
    window.PrepAIUtils = { Navigation, Validation, UI, SkillsMapping };
}
