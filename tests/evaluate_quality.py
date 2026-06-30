"""
CHATBOT QUALITY AND CORRECTNESS EVALUATION
==========================================
Why perform this test?
----------------------
While latency tests measure "speed", quality tests measure "correctness" and "safety". 
LLMs are highly non-deterministic and can produce inaccurate, toxic, or non-compliant responses if prompt drift occurs. 
This script runs automated regression tests using a "Golden Dataset" (`eval_messages.json`) to verify:

1. Factual Correctness (Factual QA):
   - Goal: Ensure the chatbot accurately explains domain-specific topics.
   - Test Detail: Checks that responses contain key technical vocabulary (e.g. "browser" and "database" for web caching).

2. System Instruction Compliance (Instruction adherence):
   - Goal: Ensure the chatbot obeys architectural constraints (such as being concise, formatting as markdown, or keeping answers to 1 sentence).
   - Test Detail: Checks sentence length, word count assertions, and output string formats.

3. Safety/Guardrails (Refusal checks & Jailbreak resistance):
   - Goal: Verify that the chatbot refuses malicious queries and rejects prompt injections.
   - Test Detail: Issues requests designed to force rule-breaking (jailbreaks) and asserts that the chatbot rejects them (e.g., matching refusal phrases like "cannot assist" and excluding injected words).

4. Chat History Retrieval (Memory):
   - Goal: Check that multi-turn session storage functions correctly on the backend.
   - Test Detail: Sends sequential messages to build a conversation thread, then queries something from the past to ensure context memory.
"""

import json
import os
import requests
import uuid
import re
from typing import Dict, Any, List


BACKEND_URL = "http://localhost:8000"
EVAL_FILE = os.path.join(os.path.dirname(__file__), "eval_messages.json")

def clean_text(text: str) -> str:
    return text.lower().strip()

def check_assertions(response_text: str, assertions: Dict[str, Any]) -> List[str]:
    failures = []
    text_lower = response_text.lower()
    
    # 1. contains_all - check if all required keywords are present
    if "contains_all" in assertions:
        for keyword in assertions["contains_all"]:
            if keyword.lower() not in text_lower:
                failures.append(f"Expected to contain '{keyword}' but was not found.")
                
    # 2. contains_any - check if at least one required keyword is present (useful for fallback matching)
    if "contains_any" in assertions:
        found = False
        for keyword in assertions["contains_any"]:
            if keyword.lower() in text_lower:
                found = True
                break
        if not found:
            failures.append(f"Expected to contain at least one of: {assertions['contains_any']}.")
            
    # 3. excludes - verify that forbidden words or leak indicators are absent
    if "excludes" in assertions:
        for keyword in assertions["excludes"]:
            if keyword.lower() in text_lower:
                failures.append(f"Expected to exclude '{keyword}' but it was found.")
                
    # 4. min_length_chars - check message richness
    if "min_length_chars" in assertions:
        min_len = assertions["min_length_chars"]
        if len(response_text) < min_len:
            failures.append(f"Response length ({len(response_text)}) is less than minimum ({min_len} chars).")
            
    # 5. max_length_chars - check verbosity restrictions
    if "max_length_chars" in assertions:
        max_len = assertions["max_length_chars"]
        if len(response_text) > max_len:
            failures.append(f"Response length ({len(response_text)}) exceeds maximum ({max_len} chars).")
            
    # 6. max_sentence_count - verify strict sentence limits
    if "max_sentence_count" in assertions:
        sentences = [s for s in re.split(r'[.!?]+', response_text) if s.strip()]
        max_sentences = assertions["max_sentence_count"]
        if len(sentences) > max_sentences:
            failures.append(f"Sentence count ({len(sentences)}) exceeds maximum ({max_sentences} sentences).")
            
    return failures

def run_evaluation() -> bool:
    if not os.path.exists(EVAL_FILE):
        print(f"Evaluation file not found at {EVAL_FILE}")
        return False
        
    with open(EVAL_FILE, "r") as f:
        test_cases = json.load(f)
        
    print(f"Loaded {len(test_cases)} test cases from {EVAL_FILE}.\n")
    
    passed_count = 0
    failed_count = 0
    
    for case in test_cases:
        case_id = case.get("id")
        category = case.get("category")
        system_instruction = case.get("system_instruction")
        messages = case.get("messages", [])
        assertions = case.get("assertions", {})
        
        print(f"Running Test Case [{case_id}] (Category: {category})...")
        
        # Fresh unique user/session IDs for isolated memory testing
        session_id = f"eval_{uuid.uuid4().hex[:8]}"
        user_id = f"eval_user_{uuid.uuid4().hex[:8]}"
        
        # Identify the user messages in the message history
        # (Mock running conversation stream to test user input sequences)
        user_prompts = [m["content"] for m in messages if m["role"] == "user"]
        
        if not user_prompts:
            print(f"Skipping test case {case_id}: no user messages found.\n")
            continue
            
        final_response_text = ""
        
        for i, prompt in enumerate(user_prompts):
            print(f"  -> Sending chunk {i+1}/{len(user_prompts)}: '{prompt}'")
            payload = {
                "message": prompt,
                "user_id": user_id,
                "session_id": session_id,
                "system_instruction": system_instruction
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/chat", json=payload, stream=True)
                if response.status_code != 200:
                    print(f"  [ERROR] Status Code {response.status_code}: {response.text}")
                    final_response_text = ""
                    break
                    
                # Collect streaming chunks
                final_response_text = ""
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        final_response_text += chunk
                        
            except Exception as e:
                print(f"  [ERROR] Connection failed: {e}")
                final_response_text = ""
                break
                
        # Evaluate the final response text
        if not final_response_text:
            print(f"  [FAIL] No response received from target endpoint.\n")
            failed_count += 1
            continue
            
        print(f"  Received: '{final_response_text.strip()}'")
        failures = check_assertions(final_response_text, assertions)
        
        if not failures:
            print(f"  [PASS] All assertions met.\n")
            passed_count += 1
        else:
            print(f"  [FAIL] Assertions failed:")
            for fail in failures:
                print(f"    - {fail}")
            print()
            failed_count += 1
            
    print("=" * 50)
    print(f"Evaluation Complete:")
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Success Rate: {passed_count / (passed_count + failed_count) * 100:.1f}%" if (passed_count + failed_count) > 0 else "0%")
    print("=" * 50)
    
    return failed_count == 0

if __name__ == "__main__":
    run_evaluation()

#most of this test code was  written by Gemini 3.5 flash