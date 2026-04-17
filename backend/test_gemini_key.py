#!/usr/bin/env python3
"""Quick test to verify if the Gemini API key is valid."""

import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from google import genai
from app.config import settings

def test_api_key():
    print("=" * 50)
    print("Testing Gemini API Key")
    print("=" * 50)
    
    # Check if key exists
    if not settings.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY is not set in .env")
        return False
    
    # Mask the key for display (but show enough to identify which key)
    key = settings.GEMINI_API_KEY
    masked = f"{key[:12]}...{key[-4:]}" if len(key) > 16 else "***"
    print(f"API Key (check this matches your teammate's): {masked}")
    print(f"Key Length: {len(key)} characters")
    print()
    
    # Test the client
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Try a simple generation
        print("Sending test request to Gemini...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents="Say 'API key is working!' if you receive this.",
        )
        
        print()
        print("✅ SUCCESS! API key is valid!")
        print(f"Response: {response.text.strip()}")
        return True
        
    except Exception as e:
        print()
        print(f"❌ FAILED! Error: {str(e)}")
        
        # Provide specific guidance based on error
        error_str = str(e).lower()
        if "permission_denied" in error_str or "403" in error_str:
            print()
            print("→ This is a 403 PERMISSION_DENIED error.")
            print("→ Your API key is invalid or the project is disabled.")
            print("→ Solution: Get a new key from https://aistudio.google.com/apikey")
        elif "api key not valid" in error_str:
            print()
            print("→ The API key format is incorrect or key was revoked.")
        elif "quota" in error_str:
            print()
            print("→ You may have exceeded your API quota.")
        
        return False

if __name__ == "__main__":
    success = test_api_key()
    print()
    print("=" * 50)
    sys.exit(0 if success else 1)
