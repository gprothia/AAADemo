---
id: ORD-002
title: Cancel an order before it ships
status: approved
owner: "@gprothia"
issue: "#6"
ui_routes: ["/orders/{id}"]
---

# ORD-002: Cancel an order before it ships

## Why
Customers sometimes change their minds after placing an order. They need to cancel it
themselves before it ships, without contacting support, and see straight away that it's
cancelled.

## Scope
- In: the owner cancelling a whole order that is still `pending`; a **Cancel order** button
  with a confirmation dialog on the order page; new order statuses `shipped` and `cancelled`;
  a `cancelled_at` timestamp; a test-only way to mark an order `shipped`.
- Out: partial cancellation (single line items), cancellation by staff, refunds/payment
  reversal, notifications, cancellation reasons, time limits, a real fulfilment/shipping flow.

## Acceptance criteria

### ORD-002-AC1 [api]
- **Given** a `pending` order owned by the requesting user
- **When** the client sends `POST /orders/{id}/cancel`
- **Then** the response is `200` with the order, `status: "cancelled"`, and a later
  `GET /orders/{id}` also returns `status: "cancelled"`

### ORD-002-AC2 [api]
- **Given** an order with `status: "shipped"`
- **When** the owner sends `POST /orders/{id}/cancel`
- **Then** the response is `409` with error code `ORDER_ALREADY_SHIPPED`, and a later
  `GET /orders/{id}` still returns `status: "shipped"`

### ORD-002-AC3 [api]
- **Given** an order that is already `cancelled`
- **When** the owner sends `POST /orders/{id}/cancel`
- **Then** the response is `409` with error code `ORDER_ALREADY_CANCELLED`

### ORD-002-AC4 [api]
- **Given** an order owned by another user (header `X-User` differs), or an unknown order ID
- **When** the client sends `POST /orders/{id}/cancel`
- **Then** the response is `404` with error code `ORDER_NOT_FOUND`, and the other user's
  order still has `status: "pending"`

### ORD-002-AC5 [ui]
- **Given** a user viewing their `pending` order on `/orders/{id}`
- **When** they click **Cancel order** and confirm with **Yes, cancel order** in the dialog
- **Then** the page shows the heading "Order cancelled", the status badge reads "Cancelled",
  and the **Cancel order** button is no longer shown

### ORD-002-AC6 [ui]
- **Given** a user viewing their `pending` order on `/orders/{id}`
- **When** they click **Cancel order** and then **Keep order** in the dialog
- **Then** the heading is still "Order received" and the status badge reads "Pending"

### ORD-002-AC7 [ui]
- **Given** a user viewing an order whose status is `shipped` or `cancelled`
- **Then** no **Cancel order** button is shown

### ORD-002-AC8 [api]
- **Given** a `pending` order owned by the requesting user
- **When** the client sends `POST /orders/{id}/cancel`
- **Then** the response has `cancelled_at`, an ISO 8601 UTC timestamp no earlier than when
  the request was sent and no later than when the response arrived; before cancelling,
  `GET /orders/{id}` returns `cancelled_at: null`

## Edge cases & errors
- Two cancel requests racing on the same order: exactly one gets `200`, the other `409`
  `ORDER_ALREADY_CANCELLED`.
- Cancelling doesn't change `items` or `total`.
- A repeat cancel is an error (`409 ORDER_ALREADY_CANCELLED`), not idempotent.
- No time limit: a `pending` order can be cancelled at any age.

## Test data
- Seeded SKU `TEST-SKU-1` priced at 10.00 (from ORD-001); tests create their own orders.
- Shipped orders: test-only `POST /test/orders/{id}/ship` sets `status: "shipped"`. It exists
  only when `SEED_TEST_DATA=true` (otherwise `404`) and is not part of the public API.

## Open questions
- [x] How does an order become `shipped`? → Add status `shipped`; tests set it with a
      test-only endpoint (#6).
- [x] Repeat cancel idempotent `200` or `409`? → `409 ORDER_ALREADY_CANCELLED` (#6).
- [x] Confirmation dialog? → Yes: **Yes, cancel order** / **Keep order** (#6).
- [x] Cancellation reason? → Not needed (#6).
- [x] Time limit? → None (#6).
- [x] Record `cancelled_at`? → Yes (#6).
- [x] Partial/staff cancellation, refunds, notifications? → Out of scope (#6).
