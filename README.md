# Legality AI - AI-Powered Contract Risk Analyzer

An intelligent contract analysis system that uses adversarial AI agents and RAG (Retrieval-Augmented Generation) to identify risky clauses in legal contracts and suggest safer alternatives.

--------------------------------------------

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [How It Works](#how-it-works)
- [Contributors](#contributors)

---

## 🎯 Overview

Legality AI analyzes legal contracts using a sophisticated pipeline powered by multiple AI agents. The system identifies risky clauses, evaluates them through adversarial analysis, and generates safer alternatives while detecting compound risks across the entire contract.

**Built as a portfolio project to demonstrate:**
- Advanced RAG implementation with semantic search
- Multi-agent AI systems with adversarial analysis
- Full-stack development with modern frameworks
- Production-grade error handling and fallback mechanisms

---

## ✨ Key Features

### Core Capabilities
- **📄 PDF Contract Analysis** - Upload and process legal contracts in PDF format
- **🤖 Adversarial AI Agents** - 3-agent system (Pessimist, Optimist, Arbiter) for balanced risk assessment
- **🔍 RAG-Powered Detection** - Semantic search against 640+ verified legal clauses
- **✍️ AI-Generated Fixes** - Automatically suggests safer alternative clauses
- **⚠️ Compound Risk Detection** - Identifies interactions between multiple risky clauses
- **📊 Interactive Dashboard** - Visual risk summary with expandable clause details
- **💬 User Feedback System** - Collect feedback to improve analysis accuracy
- **🔄 Multi-Model Fallback** - Automatic switching between AI models if one fails

---

## 🛠 Tech Stack

### Backend
- **Python 3.11** - Core programming language
- **FastAPI** - High-performance async REST API framework
- **ChromaDB** - Vector database for semantic search
- **Sentence Transformers** - Embedding generation (all-MiniLM-L6-v2)
- **OpenRouter API** - Multi-model LLM access (Claude, GPT-4, etc.)
- **PyPDF2** - PDF text extraction
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server

### Frontend
- **React 18.2** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **React Router** - Client-side routing

### AI/ML Components
- **LangChain** - LLM orchestration framework
- **Langfuse** - LLM observability (optional)
- **OpenAI SDK** - Unified API client for multiple LLM providers

### Development Tools
- **Git** - Version control
- **npm** - Frontend package management
- **pip** - Python package management
- **VS Code** - Development environment

## 📁 Project Structure
```
legality_ai/
│
├── backend/
│   ├── src/
│   │   ├── api/                    # FastAPI routes and main app
|   |   |   ├── models/
│   │   │   │   ├── requests.py     
│   │   │   │   └── responses.py                   
│   │   │   ├── routes/
│   │   │   │   ├── analysis.py     # Contract upload & analysis endpoints
│   │   │   │   ├── feedback.py     # User feedback endpoints
│   │   │   │   └── health.py       # Health check endpoint
│   │   │   └── main.py             # FastAPI application entry
│   │   │
│   │   ├── core/                   # Core models and utilities
│   │   │   ├── models.py           # Pydantic data models
│   │   │   └── llm_client.py       # Multi-model LLM client with fallback
│   │   │
│   │   ├── config/                 # Configuration
│   │   │   └── settings.py         # App settings and thresholds
│   │   │
│   │   ├── rag/                    # RAG components
│   │   │   ├── vector_store.py     # ChromaDB interface
│   │   │   ├── embeddings.py       # Embedding generation
│   │   │   └── category_detector.py # Stage 2: Category detection
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── document_processor/ # Stage 1: PDF processing
│   │   │   │   ├── pdf_processor.py
│   │   │   │   ├── metadata_extractor.py
│   │   │   │   ├── definition_extractor.py
│   │   │   │   └── semantic_chunker.py
│   │   │   │
│   │   │   ├── risk_analyzer/      # Stage 3: Adversarial analysis
│   │   │   │   ├── pessimist_agent.py
│   │   │   │   ├── optimist_agent.py
│   │   │   │   ├── arbiter_agent.py
│   │   │   │   └── adversarial_analyzer.py
│   │   │   │
│   │   │   ├── fix_generator/      # Stage 4: Fix generation
│   │   │   │   └── fix_generator.py
│   │   │   │
│   │   │   ├── compound_detector/  # Stage 5: Compound risks
│   │   │   │   └── compound_detector.py
│   │   │   │
│   │   │   ├── feedback_manager/   # Stage 6: Feedback
│   │   │   │   ├── feedback_manager.py
│   │   │   │   └── learning_loop.py
│   │   │   │
│   │   │   └── analyzer.py         # Main orchestrator
│   │   │
│   │   └── utils/                  # Utilities
│   │       └── text_utils.py
│   │
│   ├── build_pipeline/             # Vector DB construction
│   │   └── build_vector_db.py      # Build ChromaDB from CUAD dataset
│   │
│   ├── data/                       # Training data
│   │   ├── verified_golden_rules.json    # 533 safe clauses
│   │   └── extracted_clauses.json        # 107 risky clauses
│   │
│   ├── chroma_db_gold/             # Vector database (generated)
│   ├── uploads/                    # Temporary PDF storage
│   │
│   ├── .env                        # Environment variables
│   ├── requirements.txt            # Python dependencies
│   └── run.py                      # Application entry point
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── upload/             # File upload component
│   │   │   │   └── FileUploader.tsx
│   │   │   ├── viewer/             # Results display
│   │   │   │   ├── ClauseCard.tsx
│   │   │   │   └── CompactClauseCard.tsx
│   │   │   ├── risk/               # Risk visualization
│   │   │   │   ├── RiskBadge.tsx
│   │   │   │   └── RiskSummary.tsx
│   │   │   ├── feedback/           # User feedback
│   │   │   │   └── FeedbackButtons.tsx
│   │   │   └── common/             # Shared components
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.tsx        # Landing page with upload
│   │   │   └── AnalysisPage.tsx    # Results page
│   │   │
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   │
│   │   ├── hooks/
│   │   │   └── useAnalysis.ts      # Analysis polling hook
│   │   │
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript interfaces
│   │   │
│   │   ├── utils/
│   │   │   └── colors.ts           # Risk color utilities
│   │   │
│   │   ├── App.tsx                 # Main app component
│   │   ├── index.tsx               # React entry point
│   │   └── index.css               # Global styles
│   │
│   ├── .env                        # Frontend environment variables
│   ├── package.json                # Node dependencies
│   ├── tailwind.config.js          # Tailwind configuration
│   └── tsconfig.json               # TypeScript configuration
│
└── README.md                       # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm
- **OpenRouter API Key** 
- **Git**

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/legality_ai.git
cd legality_ai
```

### Step 2: Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `backend/.env`:**
```env
# Required
OPENROUTER_API_KEY=your_key_here

# Optional
LANGFUSE_ENABLED=false
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 3: Build Vector Database
```bash
# Build ChromaDB from CUAD dataset (one-time setup)
python build_pipeline/build_vector_db.py
```

**Expected output:**
```
🗃️  INITIALIZING GOLDEN STANDARD DATABASE...
    Loaded 533 safe clauses.
    Loaded 107 risky clauses.
    Indexing 640 total documents...
✅ SUCCESS! Vector DB created
```

### Step 4: Frontend Setup
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

**Edit `frontend/.env`:**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## ▶️ How to Run

### Start Backend Server
```bash
cd backend
python run.py
```

**Backend will start at:** http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Start Frontend Server
```bash
cd frontend
npm start
```

**Frontend will start at:** http://localhost:3000

### Test the System

1. Open http://localhost:3000
2. Upload a contract PDF (sample provided in `backend/data/sample_nda.pdf`)
3. Wait 30-60 seconds for analysis
4. View results with risk scores and suggested fixes

---

## 🔄 How It Works

### Stage 1: Document Processing
1. **PDF Extraction** - Extracts text from uploaded PDF
2. **Metadata Extraction** - Identifies contract type, parties, dates
3. **Definition Extraction** - Finds defined terms (e.g., "Confidential Information")
4. **Semantic Chunking** - Splits document into coherent chunks using embeddings

### Stage 2: RAG-Powered Category Detection
1. Queries vector database with each chunk
2. Matches against category prototypes (e.g., "Termination", "Liability")
3. Applies 3-zone filtering:
   - **Zone 1 (Noise):** < 30% similarity - ignore
   - **Zone 2 (Courtroom):** 30-85% similarity - needs AI review
   - **Zone 3 (Safe Check):** > 85% similarity - verify against safe standards
4. Retrieves relevant examples for context

### Stage 3: Adversarial Risk Analysis
Each risky clause is analyzed by 3 AI agents:

1. **Pessimist (Red Team):**
   - Assumes worst-case interpretation
   - Scores risk 0-100 (biased high)
   - Identifies hidden dangers

2. **Optimist (Blue Team):**
   - Finds legitimate business justifications
   - Scores defensibility 0-100
   - Identifies mitigating factors

3. **Arbiter (Judge):**
   - Reviews both arguments
   - Makes final balanced verdict
   - Assigns final risk score and level

### Stage 4: Fix Generation
- AI generates safer alternative clauses
- Maintains legal validity
- Balances both parties' interests
- Provides explanation of changes

### Stage 5: Compound Risk Detection
- Detects patterns across multiple clauses
- Examples:
  - Termination + Unlimited Liability
  - Non-Compete + Broad IP Assignment
  - Unilateral Changes + No Notice Period
- Validates patterns with LLM
- Suggests holistic mitigations

### Stage 6: User Feedback Collection
- False positive reporting
- False negative reporting
- Fix approval/rejection
- Stores feedback for future model improvement

## 🛠 Known Limitations

- This system does not replace legal professionals
- Only English-language contracts are currently supported
- Risk scores are probabilistic and AI-generated
- This is a prototype-grade system intended for research and evaluation


## 👨‍💻 Contributors

**Yashwanth N** 
      &
**Divya Yadav**

## 🙏 Acknowledgments

- **CUAD Dataset** - Contract Understanding Atticus Dataset for training data
- **OpenRouter** - Unified API access to multiple LLM providers
- **ChromaDB** - Open-source vector database
- **Sentence Transformers** - Pre-trained embedding models
- **FastAPI** - Modern Python web framework

---

**Built with ❤️ as a portfolio project showcasing AI/ML engineering and full-stack development skills**