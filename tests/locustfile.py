from locust import HttpUser, task


class ChatUser(HttpUser):
    @task
    def chat(self):
        self.client.post(
            "/chat",
            json={
                "message": "Hello",
                "user_id": "tester",
                "session_id": "test_session",
            },
        )
