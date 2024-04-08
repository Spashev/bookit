from locust import HttpUser, task


class ProductApiTest(HttpUser):
    @task
    def get_products(self):
        self.client.get("/api/v1/products/get")

    @task
    def get_product(self):
        self.client.get("/api/v1/products/1")
