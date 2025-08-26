// Production Performance Monitor for PrepAI
// Tracks performance metrics, user experience, and system health

const PerformanceMonitor = {
    // Performance metrics
    metrics: {
        pageLoadTime: 0,
        domReadyTime: 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        firstInputDelay: 0,
        timeToInteractive: 0
    },

    // User interaction tracking
    interactions: {
        clicks: 0,
        navigation: 0,
        formSubmissions: 0,
        errors: 0,
        sessionDuration: 0
    },

    // Initialize performance monitoring
    init() {
        this.setupPerformanceObservers();
        this.trackUserInteractions();
        this.startSessionTimer();
        this.monitorResourceLoading();
    },

    // Setup performance observers
    setupPerformanceObservers() {
        // Navigation Timing API
        if ('performance' in window) {
            window.addEventListener('load', () => {
                this.calculatePageLoadMetrics();
            });

            // Track DOM ready time
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.metrics.domReadyTime = performance.now();
                });
            } else {
                this.metrics.domReadyTime = performance.now();
            }
        }

        // Web Vitals
        if ('PerformanceObserver' in window) {
            // First Contentful Paint
            try {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    if (entries.length > 0) {
                        this.metrics.firstContentfulPaint = entries[entries.length - 1].startTime;
                    }
                }).observe({ entryTypes: ['paint'] });
            } catch (error) {
                // Fallback for older browsers
            }

            // Largest Contentful Paint
            try {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    if (entries.length > 0) {
                        this.metrics.largestContentfulPaint = entries[entries.length - 1].startTime;
                    }
                }).observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (error) {
                // Fallback for older browsers
            }

            // Layout Shift
            try {
                new PerformanceObserver((list) => {
                    let cumulativeShift = 0;
                    list.getEntries().forEach(entry => {
                        if (!entry.hadRecentInput) {
                            cumulativeShift += entry.value;
                        }
                    });
                    this.metrics.cumulativeLayoutShift = cumulativeShift;
                }).observe({ entryTypes: ['layout-shift'] });
            } catch (error) {
                // Fallback for older browsers
            }

            // First Input Delay
            try {
                new PerformanceObserver((list) => {
                    list.getEntries().forEach(entry => {
                        if (entry.processingStart > 0) {
                            this.metrics.firstInputDelay = entry.processingStart - entry.startTime;
                        }
                    });
                }).observe({ entryTypes: ['first-input'] });
            } catch (error) {
                // Fallback for older browsers
            }
        }
    },

    // Calculate page load metrics
    calculatePageLoadMetrics() {
        if ('performance' in window && 'timing' in performance) {
            const timing = performance.timing;
            this.metrics.pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            this.metrics.timeToInteractive = timing.domInteractive - timing.navigationStart;
        } else if ('performance' in window && 'getEntriesByType' in performance) {
            // Modern Performance API
            const navigationEntries = performance.getEntriesByType('navigation');
            if (navigationEntries.length > 0) {
                const navEntry = navigationEntries[0];
                this.metrics.pageLoadTime = navEntry.loadEventEnd - navEntry.startTime;
                this.metrics.timeToInteractive = navEntry.domInteractive - navEntry.startTime;
            }
        }
    },

    // Track user interactions
    trackUserInteractions() {
        // Click tracking
        document.addEventListener('click', (event) => {
            this.interactions.clicks++;
            this.trackElementInteraction(event.target, 'click');
        });

        // Navigation tracking
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function(...args) {
            PerformanceMonitor.interactions.navigation++;
            PerformanceMonitor.trackPageNavigation('pushState', args[2]);
            return originalPushState.apply(this, args);
        };
        
        history.replaceState = function(...args) {
            PerformanceMonitor.interactions.navigation++;
            PerformanceMonitor.trackPageNavigation('replaceState', args[2]);
            return originalReplaceState.apply(this, args);
        };

        // Form submission tracking
        document.addEventListener('submit', (event) => {
            this.interactions.formSubmissions++;
            this.trackFormSubmission(event.target);
        });
    },

    // Track element interaction
    trackElementInteraction(element, action) {
        const interactionData = {
            timestamp: Date.now(),
            action: action,
            element: element.tagName?.toLowerCase() || 'unknown',
            elementId: element.id || 'none',
            elementClass: element.className || 'none',
            page: window.location.pathname
        };

        this.storeInteractionData(interactionData);
    },

    // Track page navigation
    trackPageNavigation(method, url) {
        const navigationData = {
            timestamp: Date.now(),
            method: method,
            from: window.location.pathname,
            to: url || 'unknown',
            sessionId: window.prepAIState?.sessionId || 'none'
        };

        this.storeInteractionData(navigationData);
    },

    // Track form submission
    trackFormSubmission(form) {
        const formData = {
            timestamp: Date.now(),
            formId: form.id || 'none',
            formAction: form.action || 'none',
            formMethod: form.method || 'none',
            page: window.location.pathname
        };

        this.storeInteractionData(formData);
    },

    // Store interaction data
    storeInteractionData(data) {
        try {
            const interactions = JSON.parse(sessionStorage.getItem('prepai_interactions') || '[]');
            interactions.push(data);
            
            // Keep only last 100 interactions
            if (interactions.length > 100) {
                interactions.splice(0, interactions.length - 100);
            }
            
            sessionStorage.setItem('prepai_interactions', JSON.stringify(interactions));
        } catch (error) {
            // Fallback: just log to console
            console.warn('Failed to store interaction data:', error);
        }
    },

    // Start session timer
    startSessionTimer() {
        this.sessionStartTime = Date.now();
        
        // Update session duration every minute
        setInterval(() => {
            this.interactions.sessionDuration = Date.now() - this.sessionStartTime;
        }, 60000);

        // Track session end
        window.addEventListener('beforeunload', () => {
            this.interactions.sessionDuration = Date.now() - this.sessionStartTime;
            this.sendPerformanceReport();
        });
    },

    // Monitor resource loading
    monitorResourceLoading() {
        // Track resource load times
        const resources = performance.getEntriesByType('resource');
        let totalLoadTime = 0;
        let slowResources = [];

        resources.forEach(resource => {
            totalLoadTime += resource.duration;
            
            if (resource.duration > 2000) { // Resources taking more than 2 seconds
                slowResources.push({
                    name: resource.name,
                    duration: resource.duration,
                    size: resource.transferSize || 0
                });
            }
        });

        // Store resource performance data
        this.resourceMetrics = {
            totalResources: resources.length,
            totalLoadTime: totalLoadTime,
            averageLoadTime: totalLoadTime / resources.length,
            slowResources: slowResources
        };
    },

    // Generate performance report
    generatePerformanceReport() {
        return {
            timestamp: new Date().toISOString(),
            page: window.location.pathname,
            sessionId: window.prepAIState?.sessionId || 'none',
            metrics: this.metrics,
            interactions: this.interactions,
            resourceMetrics: this.resourceMetrics,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            memory: performance.memory ? {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            } : null
        };
    },

    // Send performance report
    sendPerformanceReport() {
        const report = this.generatePerformanceReport();
        
        // Store locally for debugging
        try {
            const reports = JSON.parse(sessionStorage.getItem('prepai_performance_reports') || '[]');
            reports.push(report);
            
            // Keep only last 10 reports
            if (reports.length > 10) {
                reports.splice(0, reports.length - 10);
            }
            
            sessionStorage.setItem('prepai_performance_reports', JSON.stringify(reports));
        } catch (error) {
            console.warn('Failed to store performance report:', error);
        }

        // Send to monitoring service in production
        if (window.PREPAI_CONFIG?.ENVIRONMENT === 'production') {
            try {
                fetch('/api/performance-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(report)
                }).catch(() => {
                    // Silently fail if monitoring service is unavailable
                });
            } catch (error) {
                // Ignore monitoring errors
            }
        }
    },

    // Get performance score (0-100)
    getPerformanceScore() {
        let score = 100;
        
        // Deduct points for slow loading
        if (this.metrics.pageLoadTime > 3000) score -= 20;
        if (this.metrics.pageLoadTime > 5000) score -= 30;
        
        // Deduct points for poor Core Web Vitals
        if (this.metrics.firstContentfulPaint > 1500) score -= 15;
        if (this.metrics.largestContentfulPaint > 2500) score -= 15;
        if (this.metrics.cumulativeLayoutShift > 0.1) score -= 10;
        if (this.metrics.firstInputDelay > 100) score -= 10;
        
        return Math.max(0, score);
    },

    // Log performance summary
    logPerformanceSummary() {
        const score = this.getPerformanceScore();
        console.log(`📊 Performance Score: ${score}/100`);
        console.log(`⏱️ Page Load Time: ${this.metrics.pageLoadTime.toFixed(0)}ms`);
        console.log(`🎯 First Contentful Paint: ${this.metrics.firstContentfulPaint.toFixed(0)}ms`);
        console.log(`🖱️ User Interactions: ${this.interactions.clicks} clicks, ${this.interactions.navigation} navigations`);
    }
};

// Initialize performance monitoring
if (typeof window !== 'undefined') {
    PerformanceMonitor.init();
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceMonitor;
} else {
    window.PrepAIPerformance = PerformanceMonitor;
}
