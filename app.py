import os
import logging
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from know_me_py import build_knowledge_base

load_dotenv()

# ── Configure logging ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── Build knowledge base once on startup ──────────────────────
logger.info("Initializing application...")
vector_store = build_knowledge_base()
logger.info("Application ready!")

def get_groq_client():
    """Get Groq client using API key from environment"""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        logger.error("GROQ_API_KEY not found in environment")
    return Groq(api_key=key)

def retrieve_context(question):
    """
    Retrieve relevant chunks from knowledge base
    based on the user's question using RAG
    """
    logger.info(f"Retrieving context for question: {question[:50]}...")
    results = vector_store.similarity_search(question, k=3)
    context = "\n".join([r.page_content for r in results])
    logger.info(f"Retrieved {len(results)} relevant chunks")
    return context

@app.route("/")
def index():
    logger.info("Home page requested")
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat requests from the portfolio AI.
    Uses RAG to retrieve relevant context before answering.
    """
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        logger.warning("Empty message received")
        return jsonify({"error": "No message provided"}), 400

    logger.info(f"Chat message received: {user_message[:50]}...")

    # Retrieve relevant context from knowledge base
    context = retrieve_context(user_message)

    # Build system prompt with retrieved context
    system_prompt = f"""
    You are an AI assistant representing Rahul Matai's portfolio.
    Answer questions as if you are speaking on Rahul's behalf.
    Be professional, friendly and concise.
    
    Use this context about Rahul to answer questions:
    {context}
    
    Rules:
    - Only answer questions about Rahul's experience, skills and projects
    - If asked something unrelated, politely redirect to Rahul's work
    - Keep answers concise — 2-3 sentences max unless more detail is needed
    - Speak in third person e.g. "Rahul has experience in..."
    -  NEVER share personal contact details like phone number or email
    - Instead say "You can connect with Rahul via LinkedIn or the contact form"
    """

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()
        logger.info("Response generated successfully")
        return jsonify({"response": answer})

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return jsonify({"error": "Failed to generate response"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)