import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Discount Service")

class DiscountRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    promo_code: str | None = None

class DiscountResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    discount_percent: float
    discount_reason: str

PROMO_CODES: dict[str, float] = {
    "STUDENT10": 10.0,
    "VIP20": 20.0,
    "WELCOME5": 5.0, }

BULK_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 15.0

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "discount-service"}


@app.post("/discounts/calculate", response_model=DiscountResponse)
def calculate_discount(request: DiscountRequest) -> DiscountResponse:

    discount_percent = 0.0
    reason = "No discount applied"

    if request.promo_code:
        code = request.promo_code.upper()
        if code in PROMO_CODES:
            discount_percent = PROMO_CODES[code]
            reason = f"Promo code '{request.promo_code}' applied"
        else:
            reason = f"Promo code '{request.promo_code}' is invalid"

    if discount_percent == 0.0 and request.quantity >= BULK_THRESHOLD:
        discount_percent = BULK_DISCOUNT_PERCENT
        reason = f"Bulk discount: quantity {request.quantity} >= {BULK_THRESHOLD}"

    return DiscountResponse(
        product_id=request.product_id,
        quantity=request.quantity,
        unit_price=request.unit_price,
        discount_percent=discount_percent,
        discount_reason=reason, )