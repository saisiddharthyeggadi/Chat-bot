"""
CHATBOT LATENCY BENCHMARKING
===========================
1. Time to First Token (TTFT):
2. Total Latency:
3. Time Per Output Token (TPOT):less than 50ms per token the stream generates faster than a human can read
4. Throughput (Tokens per Second):
"""

import time
import requests
import json
from typing import Dict, Any


BACKEND_URL = "http://localhost:8000"

def run_latency_benchmark(prompt: str, user_id: str = "benchmark_user", session_id: str = "benchmark_session") -> Dict[str, Any]:
    url = f"{BACKEND_URL}/chat"
    payload = {
        "message": prompt,
        "user_id": user_id,
        "session_id": session_id,
        "system_instruction": "You are a helpful assistant."
    }

    print(f"\nSending prompt: '{prompt}'")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, stream=True)
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to backend at {url}. Is the backend running?")
        print(f"Error: {e}")
        return {}

    if response.status_code != 200:
        print(f"Error response from server: {response.status_code}")
        print(response.text)
        return {}

    first_chunk_time = None
    last_chunk_time = None
    chunks_received = 0
    total_characters = 0
    full_text = ""

    # Iterate through streaming response
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if not chunk:
            continue
            
        current_time = time.time()
        
        if first_chunk_time is None:
            first_chunk_time = current_time
            print("First chunk received...")

        last_chunk_time = current_time
        chunks_received += 1
        total_characters += len(chunk)
        full_text += chunk

    end_time = time.time()
    
    if first_chunk_time is None:
        print("Received no content from stream.")
        return {}

    # Metrics calculation
    ttft = first_chunk_time - start_time
    total_duration = end_time - start_time
    streaming_duration = last_chunk_time - first_chunk_time
    
    # 1 token is roughly 4 characters on average for English text
    estimated_tokens = total_characters / 4.0
    
    # Time Per Output Token (TPOT)
    # We measure this across the streaming phase (from first to last chunk)
    if estimated_tokens > 1 and streaming_duration > 0:
        tpot = streaming_duration / (estimated_tokens - 1)
    else:
        tpot = 0.0

    tokens_per_second = estimated_tokens / total_duration if total_duration > 0 else 0

    metrics = {
        "ttft_sec": ttft,
        "tpot_sec_per_token": tpot,
        "total_latency_sec": total_duration,
        "estimated_tokens": estimated_tokens,
        "tokens_per_sec": tokens_per_second,
        "chunks_count": chunks_received,
        "response_text_length": len(full_text)
    }

    print("-" * 50)
    print(f"Latency Results (Time in seconds):")
    print(f"  - Time to First Token (TTFT):   {ttft:.3f}s")
    print(f"  - Total Latency:                {total_duration:.3f}s")
    print(f"  - Time Per Output Token (TPOT): {tpot * 1000:.1f}ms")
    print(f"  - Throughput (estimated):       {tokens_per_second:.1f} tokens/s")
    print(f"  - Estimated Tokens Generated:   {estimated_tokens:.1f}")
    print(f"  - Response Length:              {len(full_text)} characters")
    print("-" * 50)
    
    return metrics

if __name__ == "__main__":
    # Test prompt
    prompt = "Explain in 3 detailed paragraphs how caching works in web applications."
    run_latency_benchmark(prompt)


#most of this test code was  written by Gemini 3.5 flash