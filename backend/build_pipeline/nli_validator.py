import json
import os
import numpy as np
from sentence_transformers import CrossEncoder


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Points to backend/
DATA_PATH = os.path.join(BASE_DIR, "data", "golden_benchmark.json")

CATEGORY_MAP = {
    "Unilateral Termination": "Termination for Convenience",
    "Unlimited Liability": "Uncapped Liability",
    "Non-Compete": "Non Compete"
}

model = None
CACHED_DATA = {}

def load_resources():
    global model, CACHED_DATA
    if model is None:
        print("⚖️  Loading DeBERTa NLI Model (Judge)...")
        model = CrossEncoder('cross-encoder/nli-deberta-v3-base')
    
    if not CACHED_DATA:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                CACHED_DATA = json.load(f)
        else:
            print(f"❌ CRITICAL ERROR: Could not find data file at {DATA_PATH}")
            print("   Make sure 'golden_benchmark.json' is inside the 'data' folder!")

def validate_safety(safe_draft, category):
    load_resources()
    
    json_key = CATEGORY_MAP.get(category, category)
    
    category_data = CACHED_DATA.get(json_key, [])
    
    if not category_data:

        return False
        
    risk_hypothesis = category_data[0].get('hypothesis')
    
    if not risk_hypothesis:
        print(f"⚠️  Hypothesis missing in JSON for {json_key}")
        return False

    scores_array = model.predict([(safe_draft, risk_hypothesis)])
    
    logits = scores_array[0]
    
    contradiction_score = logits[0]
    entailment_score = logits[1]
    
    if contradiction_score > entailment_score and contradiction_score > 0.5:
        return True
        
    return False