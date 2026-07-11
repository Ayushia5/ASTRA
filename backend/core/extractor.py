"""Question extraction module from raw text."""
import re

def extract_questions(text: str) -> list[str]:
    """Extract distinct questions from text using heuristic patterns."""
    lines = text.splitlines()
    raw_questions = []
    
    # Patterns: starts with digit+dot (1.), starts with Q+digit (Q1), starts with "Question"
    pattern = re.compile(r"^\s*(\d+\.|Q\d+|Question)", re.IGNORECASE)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if pattern.match(line):
            q_text = line
            # Include the following line after each match if it exists
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line:
                    q_text += " " + next_line
            
            # Filter out resulting strings under 15 characters
            if len(q_text) >= 15:
                raw_questions.append(q_text)
        i += 1
        
    # Deduplicate while preserving order
    seen = set()
    unique_questions = []
    for q in raw_questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)
            if len(unique_questions) == 50:
                break
                
    if not unique_questions:
        return ["No distinct questions extracted"]
        
    return unique_questions

if __name__ == "__main__":
    sample_text = """
This is a random header.
1. What is the capital of France?
It is a very beautiful city.
Q2. Explain the theory of relativity.
In simple terms, please.
Question 3 is
too short
Question 4. Describe the process of photosynthesis in detail.
And its impact on the environment.
1. What is the capital of France?
It is a very beautiful city.
"""
    print("Testing extractor on sample text:")
    print("-" * 40)
    results = extract_questions(sample_text)
    for idx, q in enumerate(results, 1):
        print(f"{idx}. {q}")
