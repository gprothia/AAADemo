---
id: ORD-001
title: Create an order
status: implemented
owner: "@gprothia"
issue: "#3"
ui_routes: ["/orders/new"]
---

# ORD-001: Create an order

## Why
Customers need to place an order for one or more catalog items and see a confirmation immediately.

## Scope
- In: creating an order with 1–50 line items; confirmation page.
- Out: payment, shipping estimates.

## Acceptance criteria

### ORD-001-AC1 [api]
- **Given** a valid item SKU with quantity 2
- **When** the client sends `POST /orders` with that line item
- **Then** the response is `201` with an `id`, `status: "pending"` and a `total` equal to unit price × 2

### ORD-001-AC2 [api]
- **Given** an order with quantity 0
- **When** the client sends `POST /orders`
- **Then** the response is `422` and the error names the field `items[0].quantity`

### ORD-001-AC3 [api]
- **Given** an order with 51 line items
- **When** the client sends `POST /orders`
- **Then** the response is `422` with error code `TOO_MANY_ITEMS`

### ORD-001-AC4 [ui]
- **Given** a user on `/orders/new`
- **When** they add one item, set quantity to 2 and click **Place order**
- **Then** they land on `/orders/{id}` and see "Order received" and the correct total

### ORD-001-AC5 [ui]
- **Given** a user on `/orders/new` with no items added
- **Then** the **Place order** button is disabled

## Edge cases & errors
- Unknown SKU → `404` with code `SKU_NOT_FOUND`.

## Test data
Seeded SKU `TEST-SKU-1` priced at 10.00.

## Open questions
- [x] Max line items? → 50.
