import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from datetime import datetime
from contextlib import asynccontextmanager

from .database import get_order, init_db, save_order
from .settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Order Service",
    lifespan=lifespan,
)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://127.0.0.1:8001",
)

DISCOUNT_SERVICE_URL = os.getenv(
    "DISCOUNT_SERVICE_URL",
    "http://127.0.0.1:8003",
)

class OrderRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    promo_code: str | None = None


class OrderResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float
    discount_percent: float
    discount_amount: float
    total: float
    discount_reason: str


class StoredOrderResponse(BaseModel):
    id: int
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float
    discount_percent: float
    discount_amount: float
    total: float
    discount_reason: str
    created_at: datetime


class ProductFromService(BaseModel):
    id: str
    name: str
    price: float
    available: bool


class DiscountFromService(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    discount_percent: float
    discount_reason: str

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "order-service"}


@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderRequest) -> OrderResponse:
    product = await fetch_product(order.product_id)

    if not product.available:
        raise HTTPException(
            status_code=400,
            detail=f"Product '{order.product_id}' is not available",
        )

    subtotal = product.price * order.quantity

    discount = await fetch_discount(
        product_id=product.id,
        quantity=order.quantity,
        unit_price=product.price,
        promo_code=order.promo_code,
    )

    discount_amount = round(subtotal * discount.discount_percent / 100, 2)
    total = round(subtotal - discount_amount, 2)

    order_id = save_order(
        {
            "product_id": product.id,
            "quantity": order.quantity,
            "unit_price": product.price,
            "subtotal": subtotal,
            "discount_percent": discount.discount_percent,
            "discount_amount": discount_amount,
            "total": total,
            "discount_reason": discount.discount_reason,
        }
    )

    return OrderResponse(
        product_id=product.id,
        quantity=order.quantity,
        unit_price=product.price,
        subtotal=subtotal,
        discount_percent=discount.discount_percent,
        discount_amount=discount_amount,
        total=total,
        discount_reason=discount.discount_reason,
    )


@app.get("/orders/{order_id}", response_model=StoredOrderResponse)
def read_order(order_id: int) -> StoredOrderResponse:
    saved_order = get_order(order_id)

    if saved_order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' was not found",)

    return StoredOrderResponse(
        id=saved_order["id"],
        product_id=saved_order["product_id"],
        quantity=saved_order["quantity"],
        unit_price=float(saved_order["unit_price"]),
        subtotal=float(saved_order["subtotal"]),
        discount_percent=float(saved_order["discount_percent"]),
        discount_amount=float(saved_order["discount_amount"]),
        total=float(saved_order["total"]),
        discount_reason=saved_order["discount_reason"],
        created_at=saved_order["created_at"],)


async def fetch_product(product_id: str) -> ProductFromService:
    url = f"{PRODUCT_SERVICE_URL}/products/{product_id}"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Product service is unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_id}' was not found",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="Product service returned an unexpected error",
        )

    return ProductFromService.model_validate(response.json())


async def fetch_discount(
    product_id: str,
    quantity: int,
    unit_price: float,
    promo_code: str | None = None,
) -> DiscountFromService:
    url = f"{DISCOUNT_SERVICE_URL}/discounts/calculate"
    payload = {
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "promo_code": promo_code,
    }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, json=payload)

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Discount service is unavailable: {exc}",) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Discount service returned an unexpected error: {response.text}",)

    return DiscountFromService.model_validate(response.json())