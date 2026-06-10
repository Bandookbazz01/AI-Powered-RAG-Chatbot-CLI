import os
import pymongo
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mongodb import MongoDBChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.database import get_vector_store
from dotenv import load_dotenv

load_dotenv()

try:
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        temperature=0.7,
        convert_system_message_to_human=False
    )
except Exception as e:
    print(f"❌ Error initializing LLM: {str(e)}")
    raise

SYSTEM_PROMPT = """You are a highly intelligent, friendly, and helpful AI assistant.
Your goal is to provide accurate, concise, and beautifully formatted responses.

STRUCTURE YOUR ANSWERS AS FOLLOWS:
1. Intro: A small, clear introduction (1-2 sentences).
2. Main Points: Cleanly formatted as 4 bullet points (or steps) if applicable.
3. Explanation: A deeper explanation, similar to how ChatGPT or Gemini would explain it.
4. Visuals & Code: If the user asks about programming, include clear code blocks. Use markdown tables or simple ASCII visual representation if it helps explain the concept.

Use the provided Context Information to inform your answers if it is relevant.
If the context doesn't contain the answer, rely on your general knowledge but don't invent facts.
Maintain a conversational tone and be polite.

Context Information:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt | llm

in_memory_store = {}
mongodb_available = None

def check_mongodb_connection(uri: str, timeout_ms: int = 2000) -> bool:
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        client.server_info()
        client.close()
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        return False
    except Exception:
        return False

def get_session_history(session_id: str):
    global mongodb_available
    MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    if mongodb_available is None:
        mongodb_available = check_mongodb_connection(MONGO_URI)
        if not mongodb_available:
            print(f"\n⚠️  Warning: Could not connect to MongoDB at {MONGO_URI}")
            print("💡 Using in-memory chat history. History will NOT persist across restarts.\n")

    if mongodb_available:
        try:
            return MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=MONGO_URI,
                database_name=os.getenv("MONGODB_DB_NAME", "chatbot_db"),
                collection_name=os.getenv("MONGODB_COLLECTION_NAME", "chat_history"),
            )
        except Exception:
            pass

    if session_id not in in_memory_store:
        in_memory_store[session_id] = InMemoryChatMessageHistory()
    return in_memory_store[session_id]

conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def generate_response(user_id: str, message: str) -> str:
    try:
        vector_store = get_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        relevant_docs = retriever.invoke(message)
        context_text = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "No specific context found."

        response = conversational_chain.invoke(
            {"input": message, "context": context_text},
            config={"configurable": {"session_id": user_id}}
        )
        
        if isinstance(response.content, list):
            text_parts = []
            for part in response.content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            return "".join(text_parts)
            
        return str(response.content)
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"
