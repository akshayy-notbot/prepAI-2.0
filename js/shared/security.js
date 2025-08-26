// Production Security Module for PrepAI
// Handles input validation, sanitization, and security best practices

const Security = {
    // Input validation patterns
    patterns: {
        role: /^[a-zA-Z\s]+$/,
        seniority: /^(Junior|Mid|Senior)$/,
        skill: /^[a-zA-Z0-9\s\(\)\-\+\,\&\:\.]+$/,
        text: /^[a-zA-Z0-9\s\(\)\-\+\,\&\:\.\!\?\"\'\;]+$/,
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    },

    // Input validation
    validateInput(input, type, maxLength = 1000) {
        if (!input || typeof input !== 'string') {
            return { valid: false, error: 'Input is required and must be a string' };
        }

        if (input.length > maxLength) {
            return { valid: false, error: `Input too long. Maximum ${maxLength} characters allowed.` };
        }

        if (input.trim().length === 0) {
            return { valid: false, error: 'Input cannot be empty' };
        }

        // Check for potentially dangerous content
        if (this.containsDangerousContent(input)) {
            return { valid: false, error: 'Input contains potentially dangerous content' };
        }

        // Type-specific validation
        if (type && this.patterns[type]) {
            if (!this.patterns[type].test(input)) {
                return { valid: false, error: `Invalid ${type} format` };
            }
        }

        return { valid: true, sanitized: this.sanitizeInput(input) };
    },

    // Check for dangerous content
    containsDangerousContent(input) {
        const dangerousPatterns = [
            /<script/i,
            /javascript:/i,
            /on\w+\s*=/i,
            /data:text\/html/i,
            /vbscript:/i,
            /expression\s*\(/i
        ];

        return dangerousPatterns.some(pattern => pattern.test(input));
    },

    // Sanitize input
    sanitizeInput(input) {
        return input
            .replace(/[<>]/g, '') // Remove < and >
            .replace(/javascript:/gi, '') // Remove javascript: protocol
            .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '') // Remove event handlers
            .trim();
    },

    // Validate interview configuration
    validateInterviewConfig(config) {
        const errors = [];

        if (!config) {
            errors.push('Configuration object is required');
            return { valid: false, errors };
        }

        // Validate role
        if (!config.role) {
            errors.push('Role is required');
        } else {
            const roleValidation = this.validateInput(config.role, 'role', 100);
            if (!roleValidation.valid) {
                errors.push(`Role: ${roleValidation.error}`);
            }
        }

        // Validate seniority
        if (!config.seniority) {
            errors.push('Seniority level is required');
        } else {
            const seniorityValidation = this.validateInput(config.seniority, 'seniority', 50);
            if (!seniorityValidation.valid) {
                errors.push(`Seniority: ${seniorityValidation.error}`);
            }
        }

        // Validate skills
        if (!config.skills || !Array.isArray(config.skills) || config.skills.length === 0) {
            errors.push('At least one skill is required');
        } else {
            config.skills.forEach((skill, index) => {
                const skillValidation = this.validateInput(skill, 'skill', 200);
                if (!skillValidation.valid) {
                    errors.push(`Skill ${index + 1}: ${skillValidation.error}`);
                }
            });
        }

        return {
            valid: errors.length === 0,
            errors,
            sanitized: errors.length === 0 ? {
                role: this.sanitizeInput(config.role),
                seniority: this.sanitizeInput(config.seniority),
                skills: config.skills.map(skill => this.sanitizeInput(skill))
            } : null
        };
    },

    // Rate limiting for API calls
    rateLimiter: {
        calls: {},
        maxCalls: 10,
        timeWindow: 60000, // 1 minute

        canMakeCall(endpoint) {
            const now = Date.now();
            const key = endpoint;

            if (!this.calls[key]) {
                this.calls[key] = [];
            }

            // Remove old calls outside time window
            this.calls[key] = this.calls[key].filter(time => now - time < this.timeWindow);

            if (this.calls[key].length >= this.maxCalls) {
                return false;
            }

            this.calls[key].push(now);
            return true;
        },

        getRemainingCalls(endpoint) {
            const now = Date.now();
            const key = endpoint;

            if (!this.calls[key]) {
                return this.maxCalls;
            }

            this.calls[key] = this.calls[key].filter(time => now - time < this.timeWindow);
            return this.maxCalls - this.calls[key].length;
        }
    },

    // CSRF protection
    generateCSRFToken() {
        return 'csrf_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    },

    validateCSRFToken(token) {
        if (!token || typeof token !== 'string') {
            return false;
        }
        return token.startsWith('csrf_') && token.length > 20;
    }
};

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Security;
} else {
    window.PrepAISecurity = Security;
}
