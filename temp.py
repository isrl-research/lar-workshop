import os
from google import genai

def test_gemini_call():
    # 1. Pull the key from your environment
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        print("❌ ERROR: 'API_KEY' environment variable is not set.")
        return

    try:
        # 2. Initialize the client
        client = genai.Client(api_key=api_key)
        
        # 3. Make a dummy call to Gemini 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Say 'API is working!' if you can hear me."
        )
        
        print(f"✅ SUCCESS! Response from Gemini: {response.text}")
        
    except Exception as e:
        print(f"❌ API Call Failed: {e}")

if __name__ == "__main__":
    test_gemini_call()
