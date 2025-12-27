from fastapi import FastAPI
from .routers import cars, mechanics, orders, analytics

app = FastAPI(title="Autoservice REST API")

app.include_router(cars.router, prefix="/cars", tags=["cars"])
app.include_router(mechanics.router, prefix="/mechanics", tags=["mechanics"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
