"""Classifier module using Sarvam chat completions."""
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

def classify_content(text: str) -> dict:
    """Classify text risk level using Sarvam LLM."""
    if len(text) < 30:
        return {
            "classification": "unclear",
            "confidence": "low",
            "reasoning": "Insufficient text"
        }
        
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": os.getenv("SARVAM_API_KEY", ""),
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an exam integrity analyst. Classify the following text. "
        "Return ONLY valid JSON with keys: classification (one of: high_risk, "
        "possible_genuine, ghost_paper, fake_claim, unclear), confidence (high/medium/low), "
        "reasoning (max 20 words). No markdown, no backticks, raw JSON only."
    )
    
    payload = {
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": 150,
        "temperature": 0.1
    }
    
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=15.0)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # Strip markdown fences
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
            
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        
        result = json.loads(content)
        
        # Validate keys
        required_keys = {"classification", "confidence", "reasoning"}
        if not required_keys.issubset(result.keys()):
            return {
                "classification": "unclear",
                "confidence": "low",
                "reasoning": "Parse error"
            }
            
        return {
            "classification": result["classification"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"]
        }
    except Exception as e:
        print(f"[WARNING] classify_content: Classification failed - {e}")
        return {
            "classification": "unclear",
            "confidence": "low",
            "reasoning": "Classification unavailable"
        }

if __name__ == "__main__":
    sample_text = (
        "1. Solve for x: 2x + 5 = 15. Show all your working. "
        "2. What is the powerhouse of the cell? "
        "These are the leaked questions for tomorrow's Cambridge exam!"
    )
    print("Testing classifier on sample text:")
    print(sample_text)
    print("-" * 40)
    res = classify_content(sample_text)
    print("Result:", json.dumps(res, indent=2))
