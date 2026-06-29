"""
CHATBOT LOAD TESTING WITH LOCUST
================================
Why perform this test?
----------------------
Load testing evaluates the chatbot's stability, response latency, and error rates when subjected to 
realistic multi-user environments. Unlike single-user benchmarks, concurrent load tests help you identify:

1. Server Concurrency & Bottlenecks:
   - Goal: Find out how many concurrent chat streams the uvicorn backend and the Gemini API can handle.
   - Importance: Fast APIs can slow down or crash completely when multiple users connect. If connection pools
     or database handles exhaust under load, requests fail.

2. Concurrent TTFT Degradation:
   - Goal: Map how Time to First Token (TTFT) scales as active users increase.
   - Importance: When LLM token generation queues are overloaded, TTFT starts growing exponentially. Keeping
     track of TTFT under load ensures that our user experience holds up during traffic spikes.

3. Outages, Rate Limits, and Refusals (eg. HTTP 429):
   - Goal: Catch API rate limit limits from Gemini or third-party gateways.
   - Importance: Load testing triggers rate limits, letting us check if our retry backoffs (in `agent.py`) 
     work correctly under realistic pressure, and helps determine our scale-up triggers.
"""

import time
import uuid
from locust import HttpUser, task, events

class ChatUser(HttpUser):
    @task
    def chat(self):
        # Construct isolated user and session to reflect independent client requests
        user_id = f"locust_{uuid.uuid4().hex[:8]}"
        session_id = f"locust_{uuid.uuid4().hex[:8]}"
        
        start_time = time.time()
        
        # Catch and report failures manually so we can log stream performance metrics
        with self.client.post(
            "/chat",
            json={
                "message": "Provide a brief 3-sentence summary of why AI is useful.",
                "user_id": user_id,
                "session_id": session_id,
                "system_instruction": "You are a helpful summary assistant."
            },
            stream=True,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Request failed with status code {response.status_code}: {response.text}")
                return
            
            first_chunk_time = None
            total_chars = 0
            
            try:
                # Iterate and stream chunks in real-time
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                        total_chars += len(chunk)
                
                end_time = time.time()
                
                # Check if we actually received any chunks
                if first_chunk_time is None:
                    response.failure("Response was successful (200) but no data chunks were received.")
                    return
                
                # Metrics Calculation
                ttft_ms = (first_chunk_time - start_time) * 1000.0
                total_duration_ms = (end_time - start_time) * 1000.0
                
                # Fire custom Locust events to view in dashboard
                events.request.fire(
                    request_type="stream",
                    name="/chat - Time to First Token",
                    response_time=ttft_ms,
                    response_length=0
                )
                
                events.request.fire(
                    request_type="stream",
                    name="/chat - Total Generation Time",
                    response_time=total_duration_ms,
                    response_length=total_chars
                )
                
                # Mark page request as success
                response.success()
                
            except Exception as e:
                response.failure(f"Streaming error occurred: {str(e)}")
