import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_pipeline.cuad_extract import load_cuad
from build_pipeline.generator_agent import generate_safe_variations
from build_pipeline.nli_validator import validate_safety

INPUT_CACHE_PATH = "./data/extracted_clauses.json"
OUTPUT_FILE = "./data/verified_golden_rules.json"

def main():
    print("\n🚀 STARTING LEGAL AI DATA FACTORY (Multi-Variation Mode)")
    print("=======================================================")

    print("\n🔹 [Step 1] Loading Risky Clauses (CUAD)...")
    
    if os.path.exists(INPUT_CACHE_PATH):
        print(f"   Using cached data from {INPUT_CACHE_PATH}")
        with open(INPUT_CACHE_PATH, "r") as f:
            risky_samples = json.load(f)
    else:
        risky_samples = load_cuad() 
    
    print(f"   Found {len(risky_samples)} risky samples to process.")

    print("\n🔹 [Step 2] Running Generation & Validation Factory...")
    print("   (Generating 5 variations per risk -> Validating individually)")
    
    verified_pairs = []
    
    for i, sample in enumerate(risky_samples):
        category = sample['category']
        risky_text = sample['risky_text']
        
        print(f"\n[{i+1}/{len(risky_samples)}] Processing: {category}")
        
        max_retries = 3
        current_try = 0
        feedback = ""
        success_for_this_sample = False

        while current_try < max_retries:
            # A. Generate 5 Variations (The Writer)
            drafts = generate_safe_variations(risky_text, category, feedback)
            
            if not drafts:
                print("      ⚠️ Generation Error (API issue). Retrying...")
                current_try += 1
                continue

            print(f"      -> Received {len(drafts)} variations. Validating...")

            # B. Validate Each Variation (The Judge)
            valid_batch_count = 0
            
            for idx, draft in enumerate(drafts):
                if validate_safety(draft, category):
                    
                    verified_pairs.append({
                        "category": category,
                        "risky_origin": risky_text,
                        "safe_fix": draft,
                        "validation_method": "DeBERTa-NLI",
                        "style": f"Variation-{idx+1}", 
                        "attempts_needed": current_try + 1
                    })
                    valid_batch_count += 1

            if valid_batch_count > 0:
                print(f"      ✅ Success! Saved {valid_batch_count} valid variations.")
                success_for_this_sample = True
                break 
            else:
                print(f"      ❌ All {len(drafts)} variations failed validation. Retrying ({current_try+1}/{max_retries})...")
                feedback = (
                    "Your previous attempts ALL failed safety validation. "
                    "They did not sufficiently contradict the risk profile. "
                    "Ensure you explicitly state the safe/mutual terms (e.g., 'Either party may...', 'Liability is capped at...')."
                )
                current_try += 1
        
        if not success_for_this_sample:
            print("      ⚠️ SKIPPING. Could not generate any safe version after 3 retries.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(verified_pairs, f, indent=2)

    print("\n🎉 Pipeline Complete.")
    print(f"   Processed {len(risky_samples)} risky clauses.")
    print(f"   Generated {len(verified_pairs)} verified safe golden rules.")
    print(f"   💾 Database saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()