# 🔐 Environment Variables Setup for Render Deployment

## Overview
PrepAI uses environment variables for configuration, which are managed securely through Render's dashboard in production.

## 🚀 Production (Render)

### Automatic Environment Variables
These are automatically set by Render services:

- **`DATABASE_URL`**: Automatically provided by Render PostgreSQL service
- **`REDIS_URL`**: Automatically provided by Render Redis service

### Manual Environment Variables
These must be set in Render's dashboard:

- **`GOOGLE_API_KEY`**: Your Google Gemini API key
- **`ENVIRONMENT`**: Set to `production`
- **`PYTHON_VERSION`**: Set to `3.11.9`

### How to Set in Render Dashboard
1. Go to your Render service dashboard
2. Navigate to "Environment" tab
3. Add the required variables
4. Redeploy the service

## 🏠 Local Development

### Local Environment File
Create a `.env` file in your project root (never commit this file):

```bash
# Database (use local PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost/prepaidb

# Redis (use local Redis)
REDIS_URL=redis://localhost:6379/0

# Google API
GOOGLE_API_KEY=your_actual_api_key_here

# Environment
ENVIRONMENT=development
PYTHON_VERSION=3.11.9
```

### Local Testing
```bash
# Validate configuration
python verify_render_deployment.py

# Test startup
python startup.py
```

## 🔒 Security Notes

- **Never commit `.env` files** to version control
- **Never commit actual API keys** to version control
- **Use Render's secure environment variable system** for production
- **Local `.env` files** are for development only

## 📋 Validation

### Pre-Deployment
- Run validation scripts locally with `.env`
- Ensure all required variables are set in Render

### Post-Deployment
- Check startup logs for validation results
- Monitor for any configuration-related errors

## 🆘 Troubleshooting

### Common Issues
1. **Missing DATABASE_URL**: Check Render PostgreSQL service status
2. **Missing REDIS_URL**: Check Render Redis service status
3. **Invalid GOOGLE_API_KEY**: Verify API key in Render dashboard
4. **Environment not set**: Ensure ENVIRONMENT=production in Render

### Debug Commands
```bash
# Check environment variables
python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL', 'NOT_SET'))"
python -c "import os; print('REDIS_URL:', os.getenv('REDIS_URL', 'NOT_SET'))"
python -c "import os; print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY', 'NOT_SET')[:10] + '...')"
```

---

**Remember**: Environment variables are the secure way to manage configuration. Never hardcode sensitive information in your application code.
