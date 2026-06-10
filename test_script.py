import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.chat_engine import generate_response
from app.database import initialize_knowledge_base

try:
    print("🔧 Testing chatbot setup...")
    print("\n1️⃣  Initializing knowledge base...")
    initialize_knowledge_base()
    
    print("\n2️⃣  Testing chat engine...")
    response = generate_response("test_user_001", "Hello, who are you?")
    print(f"✅ Response: {response}")
    
    print("\n3️⃣  Testing follow-up message...")
    response2 = generate_response("test_user_001", "What can you help me with?")
    print(f"✅ Response: {response2}")
    
    print("\n✅ All tests passed!")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
