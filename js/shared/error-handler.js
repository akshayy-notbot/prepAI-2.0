// Production Error Handler for PrepAI
// Provides comprehensive error handling, logging, and recovery mechanisms

const ErrorHandler = {
    // Error types and their user-friendly messages
    errorMessages: {
        network: 'Network connection issue. Please check your internet connection and try again.',
        api: 'Service temporarily unavailable. Please try again in a few moments.',
        validation: 'Please check your input and try again.',
        authentication: 'Session expired. Please refresh the page and try again.',
        permission: 'You don\'t have permission to perform this action.',
        unknown: 'An unexpected error occurred. Please try again or contact support.',
        storage: 'Unable to save your progress. Please try again.',
        navigation: 'Navigation error. Please refresh the page.',
        interview: 'Interview session error. Please restart the interview.'
    },

    // Error severity levels
    severity: {
        LOW: 'low',
        MEDIUM: 'medium',
        HIGH: 'high',
        CRITICAL: 'critical'
    },

    // Error logging
    logError(error, context = {}, severity = 'medium') {
        const errorLog = {
            timestamp: new Date().toISOString(),
            message: error.message || 'Unknown error',
            stack: error.stack,
            context: context,
            severity: severity,
            userAgent: navigator.userAgent,
            url: window.location.href,
            sessionId: window.prepAIState?.sessionId || 'none'
        };

        // Log to console in development
        if (window.PREPAI_CONFIG?.DEBUG_MODE) {
            console.error('Error logged:', errorLog);
        }

        // Store in session storage for debugging
        this.storeErrorLog(errorLog);

        // Send to monitoring service in production
        this.sendToMonitoring(errorLog);

        return errorLog;
    },

    // Store error logs locally
    storeErrorLog(errorLog) {
        try {
            const logs = JSON.parse(sessionStorage.getItem('prepai_error_logs') || '[]');
            logs.push(errorLog);
            
            // Keep only last 50 errors
            if (logs.length > 50) {
                logs.splice(0, logs.length - 50);
            }
            
            sessionStorage.setItem('prepai_error_logs', JSON.stringify(logs));
        } catch (error) {
            // Fallback: just log to console
            console.error('Failed to store error log:', error);
        }
    },

    // Send error to monitoring service
    sendToMonitoring(errorLog) {
        if (!window.PREPAI_CONFIG?.ENVIRONMENT === 'production') {
            return;
        }

        // In production, you would send to your monitoring service
        // For now, we'll just store locally
        try {
            fetch('/api/error-log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errorLog)
            }).catch(() => {
                // Silently fail if monitoring service is unavailable
            });
        } catch (error) {
            // Ignore monitoring errors
        }
    },

    // Handle different types of errors
    handleError(error, context = {}) {
        let severity = this.severity.MEDIUM;
        let userMessage = this.errorMessages.unknown;

        // Determine error type and severity
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
            severity = this.severity.HIGH;
            userMessage = this.errorMessages.network;
        } else if (error.name === 'ValidationError') {
            severity = this.severity.LOW;
            userMessage = this.errorMessages.validation;
        } else if (error.name === 'AuthenticationError') {
            severity = this.severity.HIGH;
            userMessage = this.errorMessages.authentication;
        } else if (error.name === 'PermissionError') {
            severity = this.severity.HIGH;
            userMessage = this.errorMessages.permission;
        }

        // Log the error
        this.logError(error, context, severity);

        // Show user-friendly message
        this.showErrorMessage(userMessage, severity);

        // Attempt recovery based on error type
        this.attemptRecovery(error, context, severity);

        return { severity, userMessage };
    },

    // Show error message to user
    showErrorMessage(message, severity) {
        // Remove existing error messages
        const existingErrors = document.querySelectorAll('.prepai-error-message');
        existingErrors.forEach(el => el.remove());

        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = `prepai-error-message fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-md ${
            severity === this.severity.CRITICAL ? 'bg-red-600 text-white' :
            severity === this.severity.HIGH ? 'bg-orange-500 text-white' :
            severity === this.severity.MEDIUM ? 'bg-yellow-500 text-black' :
            'bg-blue-500 text-white'
        }`;

        errorDiv.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class="font-medium">${message}</span>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-current hover:opacity-75">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(errorDiv);

        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 8000);
    },

    // Attempt error recovery
    attemptRecovery(error, context, severity) {
        if (severity === this.severity.CRITICAL) {
            // Critical errors: redirect to safe page
            this.redirectToSafePage();
        } else if (severity === this.severity.HIGH) {
            // High severity: show retry option
            this.showRetryOption(context);
        } else if (severity === this.severity.MEDIUM) {
            // Medium severity: continue with degraded functionality
            this.degradeGracefully(context);
        }
    },

    // Redirect to safe page
    redirectToSafePage() {
        try {
            // Save current state
            if (window.prepAIState) {
                window.prepAIState.saveState();
            }
            
            // Redirect to homepage
            window.location.href = 'index.html';
        } catch (error) {
            // Fallback: hard refresh
            window.location.reload();
        }
    },

    // Show retry option
    showRetryOption(context) {
        const retryDiv = document.createElement('div');
        retryDiv.className = 'prepai-retry-option fixed bottom-4 right-4 z-50 p-4 bg-white rounded-lg shadow-lg border';
        retryDiv.innerHTML = `
            <div class="text-sm text-gray-700 mb-2">Something went wrong</div>
            <button onclick="window.location.reload()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Retry
            </button>
        `;
        
        document.body.appendChild(retryDiv);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (retryDiv.parentElement) {
                retryDiv.remove();
            }
        }, 10000);
    },

    // Degrade gracefully
    degradeGracefully(context) {
        // Implement graceful degradation based on context
        if (context.page === 'interview') {
            // Disable certain features but keep basic functionality
            this.disableAdvancedFeatures();
        }
    },

    // Disable advanced features
    disableAdvancedFeatures() {
        // Disable real-time features, keep basic functionality
        const advancedElements = document.querySelectorAll('[data-feature="advanced"]');
        advancedElements.forEach(el => {
            el.style.opacity = '0.5';
            el.style.pointerEvents = 'none';
        });
    },

    // Global error handler
    setupGlobalErrorHandling() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(new Error(event.reason), { type: 'unhandledPromise' });
            event.preventDefault();
        });

        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), { 
                type: 'javascript',
                filename: event.filename,
                lineno: event.lineno
            });
        });

        // Handle resource loading errors
        window.addEventListener('error', (event) => {
            if (event.target && event.target.tagName) {
                this.handleError(new Error(`Failed to load ${event.target.tagName.toLowerCase()}`), {
                    type: 'resource',
                    resource: event.target.src || event.target.href
                });
            }
        }, true);
    },

    // Validate and sanitize user inputs
    validateUserInput(input, type) {
        if (window.PrepAISecurity) {
            return window.PrepAISecurity.validateInput(input, type);
        }
        
        // Fallback validation
        return {
            valid: input && input.trim().length > 0 && input.length < 1000,
            sanitized: input ? input.trim() : ''
        };
    }
};

// Initialize global error handling
if (typeof window !== 'undefined') {
    ErrorHandler.setupGlobalErrorHandling();
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
} else {
    window.PrepAIErrorHandler = ErrorHandler;
}
