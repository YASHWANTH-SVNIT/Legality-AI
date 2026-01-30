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
- **📥 CSV Data Export** - Download complete feedback datasets for offline auditing or model fine-tuning

---

## 🛠 Tech Stack

### Backend
- **Python 3.11** - Core programming language
- **FastAPI** - High-performance async REST API framework
- **SQLite** - Persistent storage for analyses, feedback tracking, and admin actions
- **ChromaDB** - Vector database for RAG and "Gold Standard" knowledge base
- **Sentence Transformers** - Embedding generation (all-MiniLM-L6-v2)
- **OpenRouter API** - Multi-model LLM access (Claude-3, GPT-4o, etc.) with automatic fallback
- **PyPDF2** - PDF text extraction

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

## 🔄 How It Works

### Stage 1: Document Processing
- Splits PDF into coherent chunks using semantic markers.
- Extracts metadata (parties, dates) and defined terms to improve context for the LLM.

### Stage 2: RAG Filtering
- Compares each chunk against a database of 640+ legal standards.
- Uses a "courtroom" threshold to filter noise and focus only on legally ambiguous text.

### Stage 3: The Adversarial Debate Loop
- **Pessimist Agent**: Scrutinizes for maximal risk and hidden liabilities.
- **Optimist Agent**: Argues for business necessity and standard commercial context.
- **Arbiter Agent**: Evaluates both "testimonies" to assign a final, balanced risk score.

### Stage 4: Admin Improvement Loop (RAG 2.0)
1. **User Feedback**: Users flag false positives or approve fixes.
2. **Review**: Admins use the portal to deep-dive into the AI's logic (viewing the debate data).
3. **Knowledge Base Sync**: Verified safe clauses are moved from SQLite to ChromaDB, updating the system's "Gold Standard" knowledge base in real-time.

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
