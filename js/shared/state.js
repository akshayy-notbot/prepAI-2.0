// Shared State Management for PrepAI Multi-Page System
class PrepAIState {
    constructor() {
        this.storageKey = 'prepai_state';
        this.loadState();
    }

    // Load state from sessionStorage
    loadState() {
        try {
            const stored = sessionStorage.getItem(this.storageKey);
            if (stored) {
                const parsed = JSON.parse(stored);
                this.interviewConfig = parsed.interviewConfig || {};
                this.sessionId = parsed.sessionId || null;
                this.interviewId = parsed.interviewId || null;
                this.transcript = parsed.transcript || [];
                this.currentQuestionIndex = parsed.currentQuestionIndex || 0;
            } else {
                this.resetState();
            }
        } catch (error) {
            console.error('Error loading state:', error);
            this.resetState();
        }
    }

    // Save state to sessionStorage
    saveState() {
        try {
            const stateToSave = {
                interviewConfig: this.interviewConfig,
                sessionId: this.sessionId,
                interviewId: this.interviewId,
                transcript: this.transcript,
                currentQuestionIndex: this.currentQuestionIndex,
                lastUpdated: new Date().toISOString()
            };
            sessionStorage.setItem(this.storageKey, JSON.stringify(stateToSave));
        } catch (error) {
            console.error('Error saving state:', error);
        }
    }

    // Reset state to initial values
    resetState() {
        this.interviewConfig = {
            role: null,
            seniority: null,
            skills: [],
            selectedSkillName: null,
            selectedSkillDescription: null
        };
        this.sessionId = null;
        this.interviewId = null;
        this.transcript = [];
        this.currentQuestionIndex = 0;
        this.saveState();
    }

    // Update interview configuration
    updateInterviewConfig(config) {
        this.interviewConfig = { ...this.interviewConfig, ...config };
        this.saveState();
    }

    // Set session data
    setSessionData(sessionId, interviewId) {
        this.sessionId = sessionId;
        this.interviewId = interviewId;
        this.saveState();
    }

    // Add to transcript
    addToTranscript(entry) {
        this.transcript.push(entry);
        this.saveState();
    }

    // Get current state summary
    getStateSummary() {
        return {
            hasRole: !!this.interviewConfig.role,
            hasSeniority: !!this.interviewConfig.seniority,
            hasSkills: this.interviewConfig.skills && this.interviewConfig.skills.length > 0,
            isComplete: this.interviewConfig.role && this.interviewConfig.seniority && 
                       this.interviewConfig.skills && this.interviewConfig.skills.length > 0,
            sessionActive: !!this.sessionId
        };
    }

    // Check if user can proceed to next step
    canProceedTo(step) {
        switch (step) {
            case 'onboarding':
                return true; // Always accessible
            case 'dashboard':
                return this.interviewConfig.role && this.interviewConfig.seniority && 
                       this.interviewConfig.skills && this.interviewConfig.skills.length > 0;
            case 'interview':
                return this.interviewConfig.role && this.interviewConfig.seniority && 
                       this.interviewConfig.skills && this.interviewConfig.skills.length > 0;
            case 'interview':
                return this.sessionId !== null;
            default:
                return false;
        }
    }
}

// Create global instance
const prepAIState = new PrepAIState();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PrepAIState, prepAIState };
} else {
    // Browser environment
    window.prepAIState = prepAIState;
}
