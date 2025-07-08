"""
Verify that the anthropic library is working after the upgrade
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import anthropic
    print(f"✅ Anthropic library imported successfully")
    print(f"📦 Version: {anthropic.__version__}")
    
    # Check version is >= 0.45.2
    version_parts = anthropic.__version__.split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
    patch = int(version_parts[2].split('-')[0]) if len(version_parts) > 2 else 0
    
    if major > 0 or (major == 0 and minor > 45) or (major == 0 and minor == 45 and patch >= 2):
        print("✅ Version is 0.45.2 or higher - proxy issue should be fixed")
    else:
        print("⚠️ Version is still too old - please upgrade")
        sys.exit(1)
    
    # Test initialization
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No API key found in environment")
        sys.exit(1)
    
    print(f"🔑 API key found: {api_key[:10]}...")
    
    # Initialize client
    print("\n🔧 Testing client initialization...")
    client = anthropic.Anthropic(api_key=api_key)
    print("✅ Client initialized successfully!")
    
    # Test a simple API call
    print("\n🧪 Testing API call...")
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "Reply with just the word 'SUCCESS' if you receive this."}]
    )
    
    # Extract response text properly
    response_text = ""
    if message.content:
        for content_block in message.content:
            response_text += getattr(content_block, 'text', str(content_block))
    
    print(f"✅ API call successful! Response: {response_text}")
    
    if "SUCCESS" in response_text:
        print("\n🎉 Everything is working perfectly! The anthropic library is now properly configured.")
        print("🌿 The Miradi Co-Pilot LLM integration should now work!")
    else:
        print(f"\n⚠️ API call worked but got unexpected response: {response_text}")
    
except ImportError as e:
    print(f"❌ Failed to import anthropic: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
    sys.exit(1)
