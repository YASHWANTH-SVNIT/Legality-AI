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
- Multi-agent AI systems with adversarial analysis (The Debate Loop)
- Full-stack development with modern frameworks
- Production-grade error handling and fallback mechanisms
- Secure admin-led knowledge base improvement

---

## ✨ Key Features

### Core Analysis
- **📄 PDF Contract Analysis** - Upload and process legal contracts in PDF format
- **📷 OCR for Scanned Documents** - Intelligent fallback that automatically detects scanned PDFs and uses Tesseract OCR to extract text
- **🤖 Adversarial AI Agents** - 3-agent system (**Pessimist, Optimist, Arbiter**) for a balanced "Debate Loop" risk assessment
- **🔍 RAG-Powered Detection** - Semantic search against 640+ verified legal clauses from the CUAD dataset
- **✍️ AI-Generated Fixes** - Automatically suggests safer alternative clauses that balance interests
- **⚠️ Compound Risk Detection** - Identifies hidden interactions between multiple separate clauses (e.g., Termination + Unlimited Liability)
- **📊 Interactive Dashboard** - Visual risk summary with expandable clause details and severity heatmaps

### Admin & Feedback Management
- **🔐 Secure Admin Portal** - Protected dashboard for managing system intelligence
- **🗂️ Card-Based Review System** - Intuitive interface to approve or reject user-flagged safe/risky clauses
- **🧐 Analysis Deep-Dive** - Complete transparency: view the exact Pessimist argument, Optimist defense, and Arbiter reasoning for every flagged clause
- **⚡ Batch Vector Sync** - Admins can sync approved user suggestions to the vector database in bulk, requiring re-authentication for security
---

## 🛠 Tech Stack

### Backend
- **Python 3.11** - Core programming language
- **FastAPI** - High-performance async REST API framework
- **SQLite** - Persistent storage for analyses, feedback tracking, and admin actions
- **ChromaDB** - Vector database for RAG and "Gold Standard" knowledge base
- **Sentence Transformers** - Embedding generation (all-MiniLM-L6-v2)
- **OpenRouter API** - Multi-model LLM access (Claude-3, GPT-4o, etc.) with automatic fallback
- **PyPDF2 & PDFPlumber** - Hybrid PDF text extraction
- **Tesseract OCR & Poppler** - Optical Character Recognition for scanned documents

### Frontend
- **React 18.2** - UI framework
- **TypeScript** - Type-safe development
- **Vanilla CSS & Tailwind** - Modern, responsive styling with premium aesthetics
- **Axios** - Async HTTP client
- **Lucide React** - High-quality iconography

### AI/ML Components
- **LangChain** - LLM orchestration and chain management
- **Langfuse** - LLM observability and tracing
- **OpenAI SDK** - Unified interface for multiple inference providers

---

## 📁 Project Structure
```
legality_ai/
│
├── backend/
│   ├── src/
│   │   ├── api/                    # FastAPI routes and main app
│   │   │   ├── models/             # Pydantic request/response schemas
│   │   │   ├── routes/
│   │   │   │   ├── admin.py        # NEW: Admin feedback & sync routes
│   │   │   │   ├── analysis.py     # Document analysis pipeline
│   │   │   │   └── feedback.py     # Public user feedback submission
│   │   │   └── main.py             # App entry with RAG initialization
│   │   │
│   │   ├── rag/                    # RAG components
│   │   │   ├── vector_store.py     # ChromaDB & verified clause logic
│   │   │   └── category_detector.py # Semantic similarity matching
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── document_processor/ # PDF extraction & chunking
│   │   │   │   └── pdf_processor.py # Intelligent OCR Fallback Logic
│   │   │   ├── risk_analyzer/      # Adversarial "Debate Loop" logic
│   │   │   ├── fix_generator/      # Counter-clause generation
│   │   │   ├── feedback_manager/   # SQLite persistence & batch sync
│   │   │   └── analyzer.py         # Main pipeline orchestrator
│   │   │
│   │   └── database/               # SQL schema and connection logic
│   │
│   ├── data/                       # Seed data and sample contracts
│   └── run.py                      # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/              # NEW: Admin UI (FeedbackTable, Health, etc)
│   │   │   ├── upload/             # File drop-zone components
│   │   │   ├── viewer/             # Results display & card view
│   │   │   └── feedback/           # End-user reporting tools
│   │   ├── pages/
│   │   │   ├── HomePage.tsx        # Landing page
│   │   │   ├── AnalysisPage.tsx    # detailed results
│   │   │   ├── AdminPage.tsx       # Secure admin dashboard
│   │   │   └── AdminLoginPage.tsx  # Admin authentication
│   │   └── services/
│   │       └── api.ts              # Centralized API service (Axios)
│   │
│   └── package.json                # Frontend dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm
- **OpenRouter API Key** 
- **Git**
- **OCR Tools (Required for Scanned PDFs)**:
    - **Tesseract OCR**: Install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
    - **Poppler**: Install from [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)

### Step 1: Clone Repository
```bash
git clone https://github.com/YASHWANTH-SVNIT/legality_ai.git
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

# Admin Access
ADMIN_API_KEY=admin123

# OCR Configuration (Update matching your installation paths)
POPPLER_PATH="C:\Program Files\poppler-25.12.0\Library\bin"
TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"

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

### Start Backend
```bash
cd backend
python run.py
```

### Start Frontend
```bash
cd frontend
npm start
```

### Admin Access
1. Navigate to `http://localhost:3000/admin`
2. Enter the Admin Key (Default: `admin123`, configurable in `backend/.env`)
3. Review and sync clauses to update the AI's intelligence!

---

## 👨‍💻 Contributors

**Yashwanth N** 
      &
**Divya Yadav**

---

**Built with ❤️ as a portfolio project showcasing AI Multi-Agent systems and production-grade software engineering.**
