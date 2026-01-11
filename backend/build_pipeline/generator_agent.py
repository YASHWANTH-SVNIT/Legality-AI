import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS_TO_TRY = [
    "meta-llama/llama-3.1-70b-instruct:free",  
    "google/gemini-2.0-flash-exp:free",      
    "meta-llama/llama-4-maverick",
    "huggingfaceh4/zephyr-7b-beta:free"      
]

def generate_safe_variations(risky_text, category, feedback=""):
    """
    Agent: Generates 5 DISTINCT variations of a safe clause.
    Returns: A Python LIST of 5 strings.
    """
    
    if category == "Unilateral Termination":
        goal = "Rewrite this to be MUTUAL. Allow EITHER party to terminate for convenience with 30 days prior written notice."
    elif category == "Unlimited Liability":
        goal = "Rewrite this to CAP liability. Limit aggregate liability to the total fees paid in the 12 months preceding the claim."
    elif category == "Non-Compete":
        goal = "Rewrite this to REMOVE the non-compete restriction. Replace it with a standard Confidentiality obligation only. Explicitly state parties are free to compete."
    else:
        goal = "Rewrite this clause to be balanced, mutual, and commercially standard."

    base_prompt = f"""
    Act as a Senior Contract Lawyer and Legal Engineer.
    
    TASK: {goal}
    
    RISKY CLAUSE: "{risky_text}"
    
    OUTPUT REQUIREMENT:
    Generate 5 DISTINCT variations of the safe/corrected clause to ensure semantic diversity:
    1. Variation A: Formal/Traditional (Classic legal phrasing).
    2. Variation B: Plain English (Modern, easy to read).
    3. Variation C: Concise (Short and direct).
    4. Variation D: Balanced/Mutual (Emphasizing fairness).
    5. Variation E: Detailed (Comprehensive protection).
    
    FORMAT: Return ONLY a valid JSON List of strings. Do not write anything else.
    Example: ["Text of option 1", "Text of option 2", "Text of option 3", "Text of option 4", "Text of option 5"]
    """

    if feedback:
        base_prompt += f"\n\nPREVIOUS ATTEMPT ERROR:\n{feedback}\n\nEnsure the new options avoid this error."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "LegalAI_Builder"
    }
    
    for model_name in MODELS_TO_TRY:
        try:
            resp = requests.post(
                API_URL, 
                headers=headers, 
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": base_prompt}],
                    "temperature": 0.6 
                }, 
                timeout=40 
            )
            
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content'].strip()
                
                if "[" in content and "]" in content:
                    start = content.find("[")
                    end = content.rfind("]") + 1
                    json_str = content[start:end]
                    
                    try:
                        variations = json.loads(json_str)
                        if isinstance(variations, list) and len(variations) >= 3:
                            return variations
                    except json.JSONDecodeError:
                        continue 
            
            time.sleep(1)
            
        except Exception:
            continue
            
    return []