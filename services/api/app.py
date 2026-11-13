"""Orders API: the 'existing app' for the demo.

Features already live:
  CAT-001  Browse the product catalog
  ORD-001  Create an order

Storage is in-memory on purpose: every sandbox starts clean and seeded.
"""
from __future__ import annotations

import os
import uuid
from decimal import Decimal

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

MAX_LINE_ITEMS = 50

app = FastAPI(title="Orders API", version="1.0.0")

# ---------------------------------------------------------------- data

PRODUCTS: dict[str, dict] = {}
ORDERS: dict[str, dict] = {}


def seed() -> None:
    PRODUCTS.clear()
    ORDERS.clear()
    for sku, name, price in [
        ("TEST-SKU-1", "Blue Mug", "10.00"),
        ("TEST-SKU-2", "Notebook", "4.50"),
        ("TEST-SKU-3", "Desk Lamp", "32.00"),
    ]:
        PRODUCTS[sku] = {"sku": sku, "name": name, "price": float(Decimal(price))}


if os.environ.get("SEED_TEST_DATA", "true").lower() == "true":
    seed()

# ---------------------------------------------------------------- errors


def error(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message, **extra})


def _field_path(loc: tuple) -> str:
    """('body', 'items', 0, 'quantity') -> 'items[0].quantity'"""
    out = ""
    for part in loc:
        if part == "body":
            continue
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}" if out else str(part)
    return out


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    errors = [{"field": _field_path(e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return error(422, "VALIDATION_ERROR", "Request is invalid", errors=errors)


# ---------------------------------------------------------------- health


@app.get("/healthz")
def healthz():
    return {"ok": True}


# ---------------------------------------------------------------- CAT-001


@app.get("/products")
def list_products():
    return list(PRODUCTS.values())


@app.get("/products/{sku}")
def get_product(sku: str):
    if sku not in PRODUCTS:
        return error(404, "SKU_NOT_FOUND", f"Unknown SKU {sku}")
    return PRODUCTS[sku]


# ---------------------------------------------------------------- ORD-001


class LineItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)


class OrderIn(BaseModel):
    items: list[LineItem] = Field(min_length=1)


@app.post("/orders", status_code=201)
def create_order(body: OrderIn, x_user: str = Header(default="demo")):
    if len(body.items) > MAX_LINE_ITEMS:
        return error(422, "TOO_MANY_ITEMS", f"An order can have at most {MAX_LINE_ITEMS} line items")

    lines, total = [], Decimal("0")
    for item in body.items:
        product = PRODUCTS.get(item.sku)
        if not product:
            return error(404, "SKU_NOT_FOUND", f"Unknown SKU {item.sku}")
        line_total = Decimal(str(product["price"])) * item.quantity
        total += line_total
        lines.append({**item.model_dump(), "unit_price": product["price"], "line_total": float(line_total)})

    order = {
        "id": uuid.uuid4().hex[:12],
        "owner": x_user,
        "status": "pending",
        "items": lines,
        "total": float(total),
    }
    ORDERS[order["id"]] = order
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: str, x_user: str = Header(default="demo")):
    order = ORDERS.get(order_id)
    if not order or order["owner"] != x_user:
        return error(404, "ORDER_NOT_FOUND", "Order not found")
    return order
