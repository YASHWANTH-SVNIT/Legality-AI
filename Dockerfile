FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- BACKEND SETUP ---
COPY backend/requirements.txt ./backend/
WORKDIR /app/backend

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install CPU-only PyTorch (Critical for HF Spaces size/memory)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .
# Vector DB build moved to runtime (deploy_hf.py) 

# --- FRONTEND BUILD ---
WORKDIR /app/frontend
COPY frontend/package*.json ./
# Switch to npm install for better cross-platform verification
RUN npm install

COPY frontend/ .
# Set API URL to /api (relative path for same-origin)
ENV REACT_APP_API_URL="/api" 
# Disable CI to prevent warnings from failing the build
ENV CI=false
RUN npm run build

# Debug: Check if build directory exists and has content
RUN ls -la /app/frontend/build || echo "❌ Build directory missing!"

# --- FINAL SETUP ---
WORKDIR /app/backend

# Create static directory
RUN mkdir -p static

# Copy frontend build to backend static folder (safe copy)
RUN cp -r /app/frontend/build/. /app/backend/static/

# Expose Hugging Face port
EXPOSE 7860

# Run using our custom script
CMD ["python", "deploy_hf.py"]
