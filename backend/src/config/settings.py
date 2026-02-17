from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# PROJECT PATHS
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_PATH = BASE_DIR / "chroma_db_gold"
LOGS_DIR = BASE_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

# VECTOR DATABASE
COLLECTION_GOLDEN_STANDARDS = "legal_gold_standards"
COLLECTION_PROTOTYPES = "category_prototypes"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  

# TARGET CATEGORIES
TARGET_CATEGORIES = [
    "Unilateral Termination",
    "Unlimited Liability",
    "Non-Compete"
]

# SEMANTIC CHUNKING
class ChunkingConfig:
    MIN_CHUNK_LENGTH = 100       
    MAX_CHUNK_LENGTH = 800         
    SIMILARITY_THRESHOLD = 0.75    
    OVERLAP = 50                   
    
    MERGE_INCOMPLETE = True
    
    SENTENCE_ENDINGS = ['.', '!', '?', ';']

# RAG FILTERING THRESHOLDS (3-Zone Logic)
class RAGThresholds:
    NOISE_THRESHOLD = 0.44
    
    SAFE_THRESHOLD = 0.85

    PARAM_MISMATCH_THRESHOLD = 0.20  

# LLM CONFIGURATION (Primary + Fallback)
class LLMConfig:
    # 1. PRIMARY PROVIDER (Groq - Speed)
    API_KEY = os.getenv("GROQ_API_KEY") 
    BASE_URL = "https://api.groq.com/openai/v1"
    
    MODELS = {
        "fast": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "smart": ["llama-3.3-70b-versatile"],  
        "structured": ["llama-3.1-8b-instant"] 
    }
    
    # 2. FALLBACK PROVIDER (OpenRouter - Reliability)
    ENABLE_FALLBACK = True
    FALLBACK_API_KEY = os.getenv("OPENROUTER_API_KEY")
    FALLBACK_BASE_URL = "https://openrouter.ai/api/v1"
    
    FALLBACK_MODELS = {
        "fast": ["openai/gpt-4o-mini", "meta-llama/llama-3.1-8b-instruct"],
        "smart": ["openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"],
        "structured": ["openai/gpt-4o-mini"]
    }
    
    MAX_RETRIES = 2
    RETRY_DELAY = 1
    TIMEOUT = 30

# LANGFUSE OBSERVABILITY
class LangfuseConfig:
    ENABLED = os.getenv("LANGFUSE_ENABLED", "true").lower() == "true"
    PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# DOCUMENT PROCESSING
class DocumentConfig:
    SUPPORTED_FORMATS = [".pdf"]
    
    # Maximum file size (100 MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    PDF_EXTRACTOR = "hybrid" 
    
    # Metadata extraction patterns
    METADATA_PATTERNS = {
        "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "parties": r"(?:between|by and between)\s+([^,]+)\s+(?:and|&)\s+([^,]+)",
        "effective_date": r"effective\s+(?:date|as of)[:\s]+([^\n]+)",
    }

# PARAMETER EXTRACTION
class ParameterConfig:
    """Legal parameters to extract for structural comparison"""
    
    PATTERNS = {
        # Temporal
        "days": r"(\d+)\s*(?:business\s+)?days?",
        "months": r"(\d+)\s*months?",
        "years": r"(\d+)\s*years?",
        
        # Monetary
        "amount": r"\$\s*[\d,]+(?:\.\d{2})?",
        "percentage": r"(\d+(?:\.\d+)?)\s*%",
        
        # Parties
        "party_symmetry": r"(?:either|both)\s+part(?:y|ies)",
        "unilateral": r"(?:company|employer|vendor)\s+(?:may|shall|can)",
        
        # Notice
        "written_notice": r"written\s+notice",
        "notice": r"\bnotice\b",
        
        # Cause/Reason
        "for_cause": r"for\s+cause",
        "without_cause": r"without\s+cause",
        "with_or_without": r"with\s+or\s+without\s+cause",
    }

# LOGGING
class LoggingConfig:
    LEVEL = "INFO"
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    FILE = LOGS_DIR / "app.log"

class VectorDBConfig:
    """Vector database configuration"""
    DB_PATH = "./chroma_db_gold"
    COLLECTION_NAME = "legal_gold_standards"
    COLLECTION_PROTOTYPES = "category_prototypes"
    COLLECTION_FEEDBACK = "user_feedback" 
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"