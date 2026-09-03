import os

from locust import HttpUser, between, task


class RideBackendUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = os.getenv("LOCUST_TOKEN")

    @task
    def large_dataset_rides(self):
        headers = {}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self.client.get(
            "/api/rides/large-dataset/",
            headers=headers,
            name="GET /api/rides/large-dataset/",
        )