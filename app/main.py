import time
from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="SRE Demo API", version="1.0.0")


# --- Modeli (šeme za request/response) ---
class UserCreate(BaseModel):
    name: str
    email: str


class User(UserCreate):
    id: int


class OrderCreate(BaseModel):
    user_id: int
    item: str
    price: float


class Order(OrderCreate):
    id: int

# --- Prometheus metrike ---
REQUEST_COUNT = Counter(
    "http_requests_total", "Ukupan broj HTTP zahteva", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Vreme odgovora u sekundama", ["path"]
)
ERROR_COUNT = Counter("http_5xx_errors_total", "Broj 5xx gresaka", ["path"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
    REQUEST_LATENCY.labels(path).observe(duration)
    if response.status_code >= 500:
        ERROR_COUNT.labels(path).inc()
    return response


# --- "Baza" u memoriji (za demo je dovoljno) ---
users = [
    {"id": 1, "name": "Dragan", "email": "dragan@example.com"},
    {"id": 2, "name": "Milica", "email": "milica@example.com"},
]
orders = [
    {"id": 1, "user_id": 1, "item": "Laptop", "price": 1200},
    {"id": 2, "user_id": 2, "item": "Tastatura", "price": 80},
]


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/users")
def get_users():
    return users


@app.post("/api/users", status_code=201)
def create_user(user: UserCreate):
    new_user = {"id": max((u["id"] for u in users), default=0) + 1, **user.model_dump()}
    users.append(new_user)
    return new_user


@app.get("/api/orders")
def get_orders():
    return orders


@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    new_order = {"id": max((o["id"] for o in orders), default=0) + 1, **order.model_dump()}
    orders.append(new_order)
    return new_order


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
