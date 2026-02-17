FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Build or copy vector DB
RUN python build_pipeline/build_vector_db.py 

# --- FRONTEND BUILD ---
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
# Set API URL to /api (relative path for same-origin)
ENV REACT_APP_API_URL="/api" 
RUN npm run build

# --- FINAL SETUP ---
WORKDIR /app/backend

# Create static directory
RUN mkdir -p static

# Copy frontend build to backend static folder
RUN cp -r /app/frontend/build/* /app/backend/static/

# Expose Hugging Face port
EXPOSE 7860

# Run using our custom script
CMD ["python", "deploy_hf.py"]
