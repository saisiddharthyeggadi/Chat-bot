"""
CHATBOT LOAD TESTING WITH LOCUST
================================

1. Server Concurrency & Bottlenecks:
2. Concurrent TTFT Degradation:
3. Outages, Rate Limits, and Refusals (eg. HTTP 429):
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

#most of this test code was  written by Gemini 3.5 flash