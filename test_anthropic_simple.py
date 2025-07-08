"""
Simple test to debug anthropic client initialization
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment only")

try:
    import anthropic
    print(f"Anthropic library version: {anthropic.__version__}")
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found in environment")
        print("Available environment variables:")
        for key in os.environ:
            if 'ANTHROPIC' in key.upper():
                print(f"  {key}: {os.environ[key][:10]}...")
        exit(1)
    
    print(f"API key found: {api_key[:10]}...")
    
    # Try basic initialization
    print("Attempting basic client initialization...")
    try:
        # Try with only the api_key parameter
        print("Calling anthropic.Anthropic with only api_key...")
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Basic initialization successful")
        
        # Try a simple message
        print("Testing simple message...")
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print(f"✅ Message successful: {message.content[0].text[:50]}...")
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Try to see what parameters are accepted
        import inspect
        sig = inspect.signature(anthropic.Anthropic.__init__)
        print(f"Anthropic.__init__ parameters: {list(sig.parameters.keys())}")
        
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
