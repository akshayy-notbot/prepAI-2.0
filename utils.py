import os
import google.generativeai as genai

def get_gemini_client():
    """Get configured Gemini 2.0 Flash client with API key"""
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
        raise ValueError("GOOGLE_API_KEY is set to placeholder value. Please set your actual API key.")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        return model
    except Exception as e:
        raise ValueError(f"Failed to configure Gemini API: {str(e)}")

def get_gemini_client_with_temperature(temperature: float = 0.7):
    """
    Get configured Gemini 2.0 Flash client with specific temperature setting.
    
    Args:
        temperature: Controls randomness/creativity (0.0 = deterministic, 1.0 = very creative)
                    - 0.0-0.3: More consistent, focused responses
                    - 0.4-0.7: Balanced creativity and consistency (recommended for case studies)
                    - 0.8-1.0: High creativity, more varied responses
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
        raise ValueError("GOOGLE_API_KEY is set to placeholder value. Please set your actual API key.")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        return model, temperature
    except Exception as e:
        raise ValueError(f"Failed to configure Gemini API: {str(e)}")
