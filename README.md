# Legality AI - AI-Powered Contract Risk Analyzer

An intelligent contract analysis system that uses adversarial AI agents and RAG (Retrieval-Augmented Generation) to identify risky clauses in legal contracts and suggest safer alternatives.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-purple)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama_3.3-orange)

--------------------------------------------

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [The Debate Loop (Multi-Agent Analysis)](#the-debate-loop-multi-agent-analysis)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Contributors](#contributors)

---

## 🎯 Overview

Legality AI analyzes legal contracts using a sophisticated pipeline powered by multiple AI agents. The system identifies risky clauses, evaluates them through adversarial analysis, and generates safer alternatives while detecting compound risks across the entire contract.

**Built as a portfolio project to demonstrate:**
- ✅ Advanced RAG implementation with semantic search (ChromaDB + Sentence Transformers)
- ✅ Multi-agent AI systems with adversarial analysis ("The Debate Loop")
- ✅ Full-stack development with modern frameworks (FastAPI + React + TypeScript)
- ✅ Production-grade error handling, model fallback, and cost safeguards
- ✅ Secure admin-led knowledge base improvement with batch vector sync
- ✅ Intelligent OCR fallback for scanned documents
- ✅ LLM Observability with Langfuse tracing

---

## ✨ Key Features

### 📄 Document Processing
| Feature | Description |
|---------|-------------|
| **PDF Upload** | Upload and process legal contracts in PDF format |
| **Hybrid Text Extraction** | Uses PyMuPDF + PDFPlumber for maximum text recovery |
| **OCR Fallback** | Automatically detects scanned documents (<100 chars) and switches to Tesseract OCR |
| **Semantic Chunking** | Intelligently splits documents into meaningful chunks (100-800 chars) preserving sentence boundaries |

### 🤖 AI-Powered Analysis
| Feature | Description |
|---------|-------------|
| **RAG-Powered Detection** | Semantic search against 640+ verified legal clauses from the CUAD dataset |
| **3-Zone RAG Logic** | Noise filtering (< 0.44), Agent review zone (0.44-0.85), Auto-safe (> 0.85) |
| **Adversarial Debate Loop** | 3-agent system (Pessimist → Optimist → Arbiter) for balanced risk assessment |
| **Parameter Extraction** | Extracts notice periods, monetary caps, party symmetry for structural comparison |
| **Compound Risk Detection** | Identifies dangerous interactions between multiple clauses (e.g., Termination + Unlimited Liability) |
| **AI-Generated Fixes** | Automatically suggests balanced alternative clauses |

### 📊 Results & Reporting
| Feature | Description |
|---------|-------------|
| **Interactive Dashboard** | Visual risk summary with expandable clause cards |
| **Severity Heatmaps** | Color-coded risk levels (Low → Critical) |
| **Deep-Dive Modal** | View Pessimist argument, Optimist defense, and Arbiter reasoning |
| **Compound Risk Alerts** | Highlights hidden multi-clause interactions |

### 🔐 Admin & Feedback System
| Feature | Description |
|---------|-------------|
| **User Feedback Collection** | Users can report false positives or rate fix quality (👍/👎) |
| **Secure Admin Portal** | Protected dashboard for reviewing user feedback |
| **Batch Vector Sync** | Admins can sync approved corrections to ChromaDB in bulk |
| **Auto-Archival** | Fix quality reviews auto-disappear after 30 days |
| **CSV Export** | Download all feedback data for offline analysis |

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LEGALITY AI                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   UPLOAD    │───▶│   EXTRACT   │───▶│   DETECT    │───▶│   ANALYZE   │   │
│  │  (PDF/OCR)  │    │  (Chunking) │    │    (RAG)    │    │(Debate Loop)│   │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘   │
│                                                                   │          │
│                                                                   ▼          │
│                                              ┌─────────────┐    ┌──────────┐ │
│                                              │  COMPOUND   │◀───│   FIX    │ │
│                                              │   DETECT    │    │GENERATOR │ │
│                                              └──────┬──────┘    └──────────┘ │
│                                                     │                        │
│                                                     ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           RESULTS DASHBOARD                              │ │
│  │  • Risky Clauses List  • Fix Suggestions  • Compound Risks              │ │
│  │  • Debate Transparency • User Feedback    • Admin Review                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload**: User uploads a PDF contract
2. **Extract**: Hybrid extraction (PyMuPDF + PDFPlumber) with OCR fallback
3. **Chunk**: Semantic chunking preserving legal clause boundaries
4. **Detect**: RAG query against 640+ verified clauses (3-zone filtering)
5. **Analyze**: Adversarial Debate Loop (Pessimist → Optimist → Arbiter)
6. **Fix**: AI generates balanced replacement clauses
7. **Compound**: Detects dangerous clause interactions
8. **Display**: Rich interactive dashboard with transparency

---

## 🎭 The Debate Loop (Multi-Agent Analysis)

The core innovation of Legality AI is the **Adversarial Debate Loop** - a 3-agent system that ensures balanced risk assessment:

```
                    ┌─────────────────────┐
                    │   CLAUSE + CONTEXT  │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │        🔴 PESSIMIST            │
              │   "This clause is dangerous    │
              │    because..."                 │
              │   • Identifies worst-case      │
              │   • Cites risky precedents     │
              │   • Scores risk (0-100)        │
              └────────────────┬───────────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │        🟢 OPTIMIST             │
              │   "But consider that..."       │
              │   • Provides counterarguments  │
              │   • Cites safe precedents      │
              │   • Notes mitigating factors   │
              └────────────────┬───────────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │        ⚖️ ARBITER              │
              │   "After weighing both..."     │
              │   • Reaches final verdict      │
              │   • Assigns final score        │
              │   • Provides reasoning         │
              └────────────────────────────────┘
```

### Why This Matters

- **Prevents False Positives**: The Optimist challenges the Pessimist's claims
- **Prevents False Negatives**: The Pessimist ensures real risks aren't dismissed
- **Complete Transparency**: Users see the exact reasoning for every decision
- **Balanced Assessment**: Neither agent alone determines the outcome

---

## 🎯 Current Scope & Limitations

This system is a **specialized prototype** focusing on **3 High-Impact Categories**:

| Category | What It Detects | Example Risk |
|----------|-----------------|--------------|
| **Unilateral Termination** | Unfair cancellation rights | "Company may terminate at any time without cause" |
| **Unlimited Liability** | "Bet the company" exposure | "Vendor shall be liable for all damages" |
| **Non-Compete** | Restrictive post-employment covenants | "Employee shall not compete for 5 years globally" |

> 💡 **Note**: While the RAG architecture is designed to scale to hundreds of categories (the CUAD dataset has 41), this version is intentionally focused on these three to demonstrate deep adversarial reasoning.

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core programming language |
| **FastAPI** | High-performance async REST API |
| **SQLite** | Persistent storage for analyses & feedback |
| **ChromaDB** | Vector database 
| **Sentence Transformers** | Embeddings (all-MiniLM-L6-v2) |
| **Groq API** | LLM inference (Llama-3.3-70b-versatile) |
| **PyMuPDF + PDFPlumber** | Hybrid PDF extraction |
| **Tesseract + Poppler** | OCR for scanned documents |
| **Langfuse** | LLM observability and tracing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18.2** | UI framework |
| **TypeScript** | Type-safe development |
| **TailwindCSS** | Modern, responsive styling |
| **Axios** | HTTP client |
| **Lucide React** | Premium iconography |

### AI/ML Pipeline
| Component | Purpose |
|-----------|---------|
| **LLMClient** | Unified interface with model fallback & cost safeguards |
| **CategoryDetector** | RAG-based semantic category matching |
| **AdversarialAnalyzer** | 3-agent debate loop orchestration |
| **FixGenerator** | Counter-clause generation with style matching |

---

## 📁 Project Structure

```
legality_ai/
│
├── backend/
│   ├── src/
│   │   ├── api/                          # FastAPI Application
│   │   │   ├── models/                   # Pydantic schemas
│   │   │   │   ├── requests.py
│   │   │   │   └── responses.py
│   │   │   ├── routes/
│   │   │   │   ├── admin.py              # Admin feedback & sync
│   │   │   │   ├── analysis.py           # Document analysis pipeline
│   │   │   │   └── feedback.py           # User feedback submission
│   │   │   └── main.py                   # App entry & middleware
│   │   │
│   │   ├── core/                         # Core Infrastructure
│   │   │   ├── llm_client.py             # LLM wrapper with cost safeguards
│   │   │   └── models.py                 # Domain models (Pydantic)
│   │   │
│   │   ├── rag/                          # RAG Components
│   │   │   ├── vector_store.py           # ChromaDB interface
│   │   │   └── category_detector.py      # Semantic similarity matching
│   │   │
│   │   ├── services/                     # Business Logic Layer
│   │   │   ├── document_processor/
│   │   │   │   ├── pdf_processor.py      # Hybrid extraction + OCR
│   │   │   │   └── semantic_chunker.py   # Intelligent chunking
│   │   │   ├── risk_analyzer/
│   │   │   │   ├── adversarial_analyzer.py  # The Debate Loop
│   │   │   │   ├── parameter_extractor.py   # Legal parameter extraction
│   │   │   │   └── prompts.py               # Agent prompts
│   │   │   ├── fix_generator/
│   │   │   │   └── fix_generator.py      # Counter-clause generation
│   │   │   ├── compound_detector/
│   │   │   │   └── compound_detector.py  # Multi-clause risk detection
│   │   │   ├── feedback_manager/
│   │   │   │   └── feedback_manager.py   # SQLite persistence
│   │   │   └── analyzer.py               # Main pipeline orchestrator
│   │   │
│   │   ├── config/
│   │   │   └── settings.py               # Centralized configuration
│   │   │
│   │   └── database/                     # SQLite schemas
│   │
│   ├── build_pipeline/                   # Data Factory (Offline)
│   │   ├── cuad_extract.py               # CUAD dataset extraction
│   │   ├── generator_agent.py            # Safe clause generation
│   │   ├── nli_validator.py              # DeBERTa NLI validation
│   │   ├── build_vector_db.py            # ChromaDB builder
│   │   └── run.py                        # Pipeline orchestrator
│   │
│   ├── data/                             # Seed data & samples
│   │   ├── verified_golden_rules.json    # 533 safe clauses
│   │   └── extracted_clauses.json        # 107 risky clauses
│   │
│   ├── chroma_db_gold/                   # Vector database (~3.4 MB)
│   ├── requirements.txt
│   └── run.py                            # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/                    # Admin UI components
│   │   │   │   └── FeedbackTable.tsx     # Review dashboard
│   │   │   ├── upload/                   # File upload components
│   │   │   ├── viewer/                   # Results display
│   │   │   ├── feedback/                 # User feedback buttons
│   │   │   └── common/                   # Shared components
│   │   ├── pages/
│   │   │   ├── HomePage.tsx              # Landing page
│   │   │   ├── AnalysisPage.tsx          # Results dashboard
│   │   │   ├── AdminPage.tsx             # Admin portal
│   │   │   └── AdminLoginPage.tsx        # Admin authentication
│   │   ├── services/
│   │   │   └── api.ts                    # Centralized API service
│   │   └── types/                        # TypeScript interfaces
│   │
│   ├── .env.example
│   └── package.json
│
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Groq API Key | — | LLM inference |
| Tesseract OCR | Latest | Scanned PDF support |
| Poppler | Latest | PDF to image conversion |

**OCR Tools Installation:**
- **Tesseract**: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler**: [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

### Step 1: Clone Repository
```bash
git clone https://github.com/YASHWANTH-SVNIT/legality_ai.git
cd legality_ai
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

**Edit `backend/.env`:**
```env
# Required - Get from https://console.groq.com
GROQ_API_KEY=gsk_your_key_here

# Admin Access
ADMIN_API_KEY=admin123

# OCR Configuration (Update paths)
POPPLER_PATH="C:\Program Files\poppler-25.12.0\Library\bin"
TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"

# Optional - LLM Observability
LANGFUSE_ENABLED=false
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 3: Build Vector Database
```bash
python build_pipeline/build_vector_db.py
```

**Expected output:**
```
🗃️  INITIALIZING GOLDEN STANDARD DATABASE...
    Safe clauses: D:\Projects\legality_ai\backend\data\verified_golden_rules.json
    Risky clauses: D:\Projects\legality_ai\backend\data\extracted_clauses.json
    Loaded 533 safe clauses.
    Loaded 107 risky clauses.
    Indexing 640 total documents...
✅ SUCCESS! Vector DB created
```

### Step 4: Frontend Setup
```bash
cd ../frontend

npm install

cp .env.example .env
```

**Edit `frontend/.env`:**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## ▶️ How to Run

### Start Backend
```bash
cd backend
python run.py
```
Backend runs at `http://localhost:8000`

### Start Frontend
```bash
cd frontend
npm start
```
Frontend runs at `http://localhost:3000`

### Admin Access
1. Navigate to `http://localhost:3000/admin`
2. Enter the Admin Key
3. Review user feedback and sync approved corrections

---


## ⚙️ Configuration

### LLM Models (settings.py)
```python
class LLMConfig:
    MODELS = {
        "fast": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "smart": ["llama-3.3-70b-versatile"],
        "structured": ["llama-3.3-70b-versatile"]
    }
```

### RAG Thresholds
```python
class RAGThresholds:
    NOISE_THRESHOLD = 0.44      # Below = irrelevant
    SAFE_THRESHOLD = 0.85       # Above = auto-safe
```

### Target Categories
```python
TARGET_CATEGORIES = [
    "Unilateral Termination",
    "Unlimited Liability",
    "Non-Compete"
]
```

---

## 🔒 Security Features

- **Admin Authentication**: All admin endpoints require `x-api-key` header
- **Double Authentication**: Batch sync requires secondary key confirmation
- **Cost Safeguards**: Pre-flight token estimation prevents unaffordable requests
- **Model Fallback**: Automatic failover to backup models on errors
- **Rate Limit Handling**: Automatic retry with exponential backoff

---

## 👨‍💻 Contributors

**Yashwanth N** & **Divya Yadav**

---

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ as a portfolio project showcasing AI Multi-Agent systems, RAG pipelines, and production-grade software engineering.**
