// Configuration file for PrepAI Platform
// Update these values based on your deployment environment

const CONFIG = {
    // Development Environment
    development: {
        API_BASE_URL: "http://localhost:8000",
        ENVIRONMENT: "development"
    },
    
    // Production Environment (Render)
    production: {
        API_BASE_URL: "https://prepai-api.onrender.com", // Your Render backend URL
        ENVIRONMENT: "production"
    },
    
    // GitHub Pages Environment
    githubPages: {
        API_BASE_URL: "https://prepai-api.onrender.com", // Your Render backend URL
        ENVIRONMENT: "production"
    },
    
    // Custom Domain Environment
    customDomain: {
        API_BASE_URL: "https://prepai-api.onrender.com", // Your Render backend URL
        ENVIRONMENT: "production"
    }
};

// Auto-detect environment
function getCurrentConfig() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return CONFIG.development;
    } else if (hostname.includes('github.io')) {
        return CONFIG.githubPages;
    } else if (hostname === 'doaiprep.xyz') {
        return CONFIG.customDomain;
    } else if (hostname.includes('onrender.com') || hostname.includes('prepai')) {
        return CONFIG.production;
    } else {
        return CONFIG.production; // Default to production for safety
    }
}

// Export configuration
const currentConfig = getCurrentConfig();

// For use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, getCurrentConfig, currentConfig };
} else {
    // Browser environment
    window.PREPAI_CONFIG = currentConfig;
    window.PREPAI_CONFIG_FULL = CONFIG;
}
