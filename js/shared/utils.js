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
};

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Navigation, Validation, UI, SkillsMapping };
} else {
    // Browser environment
    window.PrepAIUtils = { Navigation, Validation, UI, SkillsMapping };
}
