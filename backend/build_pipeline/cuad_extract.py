import json
import os
import requests
import random
from tqdm import tqdm
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- CONFIGURATION ---
TARGET_KEYWORDS = [
    "Termination For Convenience",
    "Uncapped Liability",
    "Non-Compete"
]

MIN_CHARS = 60
MAX_CHARS = 1000 

def map_category_name(cuad_label):
    if "Termination For Convenience" in cuad_label:
        return "Unilateral Termination"
    elif "Uncapped Liability" in cuad_label:
        return "Unlimited Liability"
    elif "Non-Compete" in cuad_label:
        return "Non-Compete"
    return "Unknown"

def check_quality_with_llm(text, category):
    if not API_KEY:
        return True, text

    # --- STRICT RULES ---
    if category == "Unilateral Termination":
        risk_definition = """
        - REJECT if 'Either party' or 'Both parties' can terminate (Mutual).
        - REJECT if termination requires 'Cause' or 'Breach'.
        - ACCEPT if ONE party has the right to terminate WITHOUT CAUSE.
        """
    elif category == "Unlimited Liability":
        risk_definition = """
        - ACCEPT clauses stating liability is unlimited or uncapped.
        - ACCEPT 'Carve-outs' or 'Exceptions' to the cap (e.g., "The cap shall not apply to Indemnification/Fraud/Negligence").
        - REJECT if the text simply ESTABLISHES a cap (e.g., "Liability is limited to $1M").
        """
    elif category == "Non-Compete":
        risk_definition = """
        - ACCEPT valid non-compete obligations (time/geo scope).
        - REJECT 'Survival Clauses' (e.g., "Section 5 survives").
        - REJECT fragments.
        """
    else:
        risk_definition = "Ensure this is a complete, valid legal clause."

    prompt = f"""
    Act as a Legal Data Curator. Review this contract clause.
    Category: "{category}"

    Rules:
    {risk_definition}

    Cleaning:
    - Remove redactions [***].
    - Remove "See Exhibit A".
    - Remove internal references.

    Raw Text: "{text}"

    Return JSON ONLY:
    {{
        "is_risk": true,
        "clean_text": "Cleaned text"
    }}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}", 
        "Content-Type": "application/json",
        "HTTP-Referer": "https://legality.ai",
        "X-Title": "Legality AI"
    }
    
    payload = {
        "model": "meta-llama/llama-4-maverick", 
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
        if response.status_code != 200: return False, text

        result_str = response.json()['choices'][0]['message']['content']
        data = json.loads(result_str)

        return data.get("is_risk", False), data.get("clean_text", text)
        
    except Exception:
        return False, text 

def extract_candidates(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    candidates = []
    for doc in tqdm(data['data'], desc="Scanning Raw Data"):
        title = doc.get('title', 'Unknown')
        for para in doc['paragraphs']:
            for qa in para['qas']:
                label = qa['question']
                if any(k in label for k in TARGET_KEYWORDS):
                    if qa['answers']:
                        clause_text = qa['answers'][0]['text']
                        if MIN_CHARS < len(clause_text) < MAX_CHARS:
                            candidates.append({
                                "category": map_category_name(label),
                                "risky_text": clause_text,
                                "source_doc": title
                            })
    return candidates

def load_cuad(file_path="./data/raw_datasets/CUAD_v1.json"):
    # 1. Get ALL Candidates
    raw_candidates = extract_candidates(file_path)
    
    print(f" Found {len(raw_candidates)} candidates. Processing...")

    high_quality_data = []
    counts = {"Unilateral Termination": 0, "Unlimited Liability": 0, "Non-Compete": 0}
    
    # 3. Validation Loop
    for item in tqdm(raw_candidates, desc="Maverick AI Review"):
        category = item['category']
        
        is_risk, clean_text = check_quality_with_llm(item['risky_text'], category)
        
        if is_risk:
            item['risky_text'] = clean_text
            high_quality_data.append(item)
            if category in counts:
                counts[category] += 1
            
    print(f" Processing Complete.")
    print(f"   - Final Counts: {counts}")
    print(f"   - Total High-Quality Clauses: {len(high_quality_data)}")
    
    return high_quality_data