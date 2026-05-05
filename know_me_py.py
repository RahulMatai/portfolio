import os
import logging
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader

# ── Configure logging ──────────────────────────────────────────
# This will show timestamp, level and message in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF file.
    Returns empty string if file is unreadable.
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text += page_text
            logger.debug(f"Page {i+1}: extracted {len(page_text)} characters")
        logger.info(f"Successfully extracted {len(text)} characters from {pdf_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
        return ""

def fetch_github_data(username):
    """
    Fetch public repos from GitHub API.
    No API key needed for public data.
    Returns a text summary of all repos.
    """
    logger.info(f"Fetching GitHub data for user: {username}")
    try:
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.warning(f"GitHub API returned status {response.status_code}")
            return "GitHub data unavailable."

        repos = response.json()
        logger.info(f"Found {len(repos)} GitHub repositories")

        text = f"GitHub Profile: {username}\n\n"
        for repo in repos:
            text += f"Project: {repo['name']}\n"
            text += f"Description: {repo['description'] or 'No description'}\n"
            text += f"Language: {repo['language'] or 'Unknown'}\n"
            text += f"Stars: {repo['stargazers_count']}\n\n"

        logger.info(f"GitHub data fetched successfully — {len(text)} characters")
        return text.strip()

    except requests.exceptions.Timeout:
        logger.error("GitHub API request timed out")
        return "GitHub data unavailable — request timed out."
    except Exception as e:
        logger.error(f"Failed to fetch GitHub data: {e}")
        return "GitHub data unavailable."

def build_knowledge_base():
    """
    Combines all data sources into one FAISS vector store.
    Called once when app starts.
    """
    logger.info("Starting knowledge base build...")
    all_text = ""

    # 1. Load LinkedIn PDF
    linkedin_path = "know_me/Profile.pdf"
    if os.path.exists(linkedin_path):
        logger.info("Loading LinkedIn PDF...")
        all_text += "\n\nLINKEDIN PROFILE:\n"
        all_text += extract_pdf_text(linkedin_path)
    else:
        logger.warning(f"LinkedIn PDF not found at {linkedin_path}")

    # 2. Load Resume PDF
    resume_path = "know_me/Rahul_Matai_Resume_.pdf"
    if os.path.exists(resume_path):
        logger.info("Loading Resume PDF...")
        all_text += "\n\nRESUME:\n"
        all_text += extract_pdf_text(resume_path)
    else:
        logger.warning(f"Resume PDF not found at {resume_path}")

    # 3. Load GitHub data
    logger.info("Fetching GitHub data...")
    all_text += "\n\nGITHUB PROJECTS:\n"
    all_text += fetch_github_data("RahulMatai")

    #manual data which is necessary for recruiters
    
    # 4. Load manual context
    logger.info("Loading manual context...")
    
    all_text += "\n\n"
    all_text += get_manual_context()
    # 4. Split into chunks
    logger.info("Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(all_text)
    logger.info(f"Created {len(chunks)} chunks from {len(all_text)} total characters")

    # 5. Create embeddings and store in FAISS
    logger.info("Creating embeddings — this may take a minute...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_texts(chunks, embeddings)
    logger.info("Knowledge base built successfully!")

    return vector_store
def get_manual_context():
    """
    Hardcoded key facts about Rahul that must always be available.
    This ensures critical info is never missed by chunking.
    """
    logger.info("Loading manual context...")
    return """
RAHUL MATAI — KEY FACTS:

Education:
- Master of Science (MS) from University College Dublin, Ireland (2022-2023)
- Master's degree in Computer Science from Symbiosis Institute (2019-2021)
- Bachelor of Computer Application from Maharaja Sayajirao University (2016-2019)
- Diploma in Cyber Law from Asian School of Cyber Laws

Experience:
- 4+ years of software engineering experience
- Contract Software Engineer at none (Dec 2023 - Mar 2026) — Dublin, Ireland
- Software Developer at Microsoft (Jun 2023 - Sep 2023) — Dublin, Ireland
- Software Developer at Innovate Tax (Nov 2020 - Oct 2022) — UK
- Full-stack Developer at Multiple Companies (May 2020 - Nov 2020) — India
- Mobile App Developer at Adri IT Solutions (Dec 2018 - May 2019) — Vadodara

Skills:
- Python (Advanced), Java, JavaScript
- AI/ML: RAG, LangChain, FAISS, Groq, LLMs
- Cloud: AWS, Azure, GCP
- Databases: PostgreSQL, SQLite, Supabase, MongoDB
- Frameworks: FastAPI, Flask, Streamlit, React

Location: Vadodara, India
"""