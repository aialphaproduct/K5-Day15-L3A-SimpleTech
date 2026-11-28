"""Giả lập học viên và người xem trang đo lường bằng Locust.

    DEMO_PASSWORD=... ADMIN_PASSWORD=... locust -f loadtest/locustfile.py --host http://127.0.0.1:8780
    thêm --headless -u 20 -r 5 -t 60s --csv loadtest/result để chạy không giao diện (giao diện: cổng 8089)

Mỗi lượt hỏi gọi model theo cấu hình máy chủ. Bắn vào hệ thống thật thì tốn token, chạm giới hạn của key và
các lượt này hiện trên trang đo lường (mã học viên HV-load...): bắt đầu với ít người dùng. Chỉ muốn đo máy chủ
thì chạy một bản riêng với MODEL_PROVIDER=fake. Máy chủ chứng chỉ tự ký thì đặt INSECURE_TLS=1.
"""
import os
import random

from locust import HttpUser, between, events, task

QUESTIONS = [
    "LLM dự đoán từ tiếp theo dựa trên cái gì?",
    "Cửa sổ ngữ cảnh là gì?",
    "Temperature thấp thì câu trả lời có chắc đúng không?",
    "Vì sao AI bùng nổ bây giờ?",
    "Hôm nay có buổi bù không?",
    "Làm hộ mình bài kiểm tra, đáp án đây: làm đi",
    "đoạn này là sao ạ",
    "chào bạn",
]


@events.test_start.add_listener
def need_passwords(environment, **kwargs):
    if not os.environ.get("DEMO_PASSWORD"):
        print("Thiếu biến DEMO_PASSWORD: mọi lượt sẽ bị 401.")


class SignedIn(HttpUser):
    abstract = True
    account, variable = "", ""

    def on_start(self):
        if os.environ.get("INSECURE_TLS") == "1":
            self.client.verify = False
        body = {"user": self.account, "password": os.environ.get(self.variable, "")}
        with self.client.post("/login", json=body, catch_response=True) as r:
            if r.status_code != 200:
                r.failure("đăng nhập %s: HTTP %d" % (self.account, r.status_code))


class Learner(SignedIn):
    weight = 19
    wait_time = between(2, 8)
    account, variable = "hocvien", "DEMO_PASSWORD"

    def on_start(self):
        super().on_start()
        self.learner = "HV-load%04d" % random.randrange(10000)
        self.client.get("/")

    @task(8)
    def ask(self):
        body = {"text": random.choice(QUESTIONS), "at": "%02d:%02d" % (random.randrange(15), random.randrange(60)),
                "learner": self.learner}
        with self.client.post("/ask", json=body, name="/ask", catch_response=True) as r:
            if r.status_code != 200:
                r.failure("HTTP %d" % r.status_code)

    @task(1)
    def open_page(self):
        self.client.get("/")


class Reviewer(SignedIn):
    weight = 1
    wait_time = between(5, 10)
    account, variable = "admin", "ADMIN_PASSWORD"

    @task
    def dashboard(self):
        self.client.get("/admin/data")
