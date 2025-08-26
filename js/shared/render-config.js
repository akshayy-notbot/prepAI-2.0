// Render-Compatible Configuration for PrepAI
// Dynamically adapts to Render environment variables and service URLs

const RenderConfig = {
    // Environment detection
    getEnvironment() {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'development';
        } else if (hostname.includes('onrender.com')) {
            return 'render';
        } else if (hostname.includes('github.io')) {
            return 'github-pages';
        } else {
            return 'production';
        }
    },

    // Get API configuration based on environment
    getAPIConfig() {
        const env = this.getEnvironment();
        
        switch (env) {
            case 'development':
                return {
                    API_BASE_URL: 'http://localhost:8000',
                    WS_BASE_URL: 'ws://localhost:8000',
                    ENVIRONMENT: 'development',
                    DEBUG_MODE: true,
                    LOG_LEVEL: 'debug'
                };
                
            case 'render':
                return {
                    API_BASE_URL: this.getRenderAPIURL(),
                    WS_BASE_URL: this.getRenderWSURL(),
                    ENVIRONMENT: 'production',
                    DEBUG_MODE: false,
                    LOG_LEVEL: 'error'
                };
                
            case 'github-pages':
                return {
                    API_BASE_URL: this.getRenderAPIURL(),
                    WS_BASE_URL: this.getRenderWSURL(),
                    ENVIRONMENT: 'production',
                    DEBUG_MODE: false,
                    LOG_LEVEL: 'error'
                };
                
            default:
                return {
                    API_BASE_URL: this.getRenderAPIURL(),
                    WS_BASE_URL: this.getRenderWSURL(),
                    ENVIRONMENT: 'production',
                    DEBUG_MODE: false,
                    LOG_LEVEL: 'error'
                };
        }
    },

    // Get Render API URL dynamically
    getRenderAPIURL() {
        // Try to get from environment or use fallback
        if (window.RENDER_API_URL) {
            return window.RENDER_API_URL;
        }
        
        // Check if we're on Render and can infer the URL
        if (window.location.hostname.includes('onrender.com')) {
            // If frontend is on Render, backend is likely on same domain
            const frontendDomain = window.location.hostname;
            const backendDomain = frontendDomain.replace('prepai-frontend', 'prepai-api');
            return `https://${backendDomain}`;
        }
        
        // Fallback to your current Render URL
        return 'https://prepai-api.onrender.com';
    },

    // Get Render WebSocket URL
    getRenderWSURL() {
        const apiURL = this.getRenderAPIURL();
        return apiURL.replace('https://', 'wss://').replace('http://', 'ws://');
    },

    // Get full configuration
    getConfig() {
        const apiConfig = this.getAPIConfig();
        
        return {
            ...apiConfig,
            
            // Performance settings
            CACHE_ENABLED: true,
            COMPRESSION_ENABLED: true,
            
            // Security settings
            HTTPS_REQUIRED: apiConfig.ENVIRONMENT === 'production',
            CORS_ENABLED: true,
            
            // Feature flags
            FEATURES: {
                advancedAnalytics: true,
                realTimeUpdates: true,
                offlineSupport: false,
                renderCompatible: true
            },
            
            // Render-specific settings
            RENDER: {
                environment: this.getEnvironment(),
                frontendURL: window.location.origin,
                backendURL: apiConfig.API_BASE_URL,
                websocketURL: apiConfig.WS_BASE_URL
            }
        };
    },

    // Initialize configuration
    init() {
        const config = this.getConfig();
        
        // Set global config
        window.PREPAI_CONFIG = config;
        
        // Log configuration in development
        if (config.DEBUG_MODE) {
            console.log('🔧 Render Config Initialized:', config);
        }
        
        return config;
    },

    // Update configuration (useful for dynamic updates)
    updateConfig(newConfig) {
        const currentConfig = window.PREPAI_CONFIG || {};
        const updatedConfig = { ...currentConfig, ...newConfig };
        
        window.PREPAI_CONFIG = updatedConfig;
        
        if (updatedConfig.DEBUG_MODE) {
            console.log('🔧 Config Updated:', updatedConfig);
        }
        
        return updatedConfig;
    },

    // Health check for Render services
    async checkRenderHealth() {
        try {
            const config = this.getConfig();
            const response = await fetch(`${config.API_BASE_URL}/health`);
            
            if (response.ok) {
                return { status: 'healthy', url: config.API_BASE_URL };
            } else {
                return { status: 'unhealthy', url: config.API_BASE_URL, statusCode: response.status };
            }
        } catch (error) {
            return { status: 'error', url: config.API_BASE_URL, error: error.message };
        }
    },

    // Get service status
    async getServiceStatus() {
        const health = await this.checkRenderHealth();
        
        return {
            environment: this.getEnvironment(),
            frontend: 'healthy',
            backend: health.status,
            timestamp: new Date().toISOString(),
            config: this.getConfig()
        };
    }
};

// Auto-initialize when loaded
if (typeof window !== 'undefined') {
    RenderConfig.init();
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RenderConfig;
} else {
    window.PrepAIRenderConfig = RenderConfig;
}
