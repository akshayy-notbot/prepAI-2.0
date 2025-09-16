// Production Configuration for PrepAI - Custom Domain
// This file contains production-optimized settings for doaiprep.xyz

window.PREPAI_CONFIG = {
    // Production API endpoints
    API_BASE_URL: 'https://prepai-api.onrender.com',
    WS_BASE_URL: 'wss://prepai-api.onrender.com',
    
    // Production settings
    ENVIRONMENT: 'production',
    DEBUG_MODE: false,
    LOG_LEVEL: 'error', // Only log errors in production
    
    // Performance settings
    CACHE_ENABLED: true,
    COMPRESSION_ENABLED: true,
    
    // Security settings
    HTTPS_REQUIRED: true,
    CORS_ENABLED: true,
    
    // Feature flags
    FEATURES: {
        advancedAnalytics: true,
        realTimeUpdates: true,
        offlineSupport: false
    }
};

// Production error handling
window.addEventListener('error', function(event) {
    if (window.PREPAI_CONFIG.LOG_LEVEL === 'error') {
        console.error('Production Error:', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error
        });
    }
});

// Production performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        if (loadTime > 5000) { // Log slow loads
            console.warn('Slow page load detected:', loadTime + 'ms');
        }
    });
}
