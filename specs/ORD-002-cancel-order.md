---
id: ORD-002
title: Cancel an order before it ships
status: draft
owner: "@gprothia"
issue: "TBD"
ui_routes: ["/orders/{id}"]
---

# ORD-002: Cancel an order before it ships

## Why
Customers sometimes change their minds after placing an order. They need to cancel it
themselves while it hasn't shipped, without contacting support, and see right away that it's
cancelled.

## Scope
- In: the owner cancelling a whole order that is still `pending`; a **Cancel order** control
  on the order page; a new order status `cancelled`.
- Out: partial cancellation (single line items), refunds/payment reversal (ORD-001 has no
  payment), cancelling shipped orders (returns), cancellation by staff, notifications.

## Acceptance criteria

### ORD-002-AC1 [api]
- **Given** a `pending` order owned by the requesting user
- **When** the client sends `POST /orders/{id}/cancel`
- **Then** the response is `200` with the order, `status: "cancelled"`, and a later
  `GET /orders/{id}` also returns `status: "cancelled"`

### ORD-002-AC2 [api]
- **Given** an order with `status: "shipped"`
- **When** the owner sends `POST /orders/{id}/cancel`
- **Then** the response is `409` with error code `ORDER_ALREADY_SHIPPED`, and the order's
  status is still `"shipped"`

### ORD-002-AC3 [api]
- **Given** an order that is already `cancelled`
- **When** the owner sends `POST /orders/{id}/cancel`
- **Then** the response is `409` with error code `ORDER_ALREADY_CANCELLED`

### ORD-002-AC4 [api]
- **Given** an order owned by another user (header `X-User` differs), or an unknown order ID
- **When** the client sends `POST /orders/{id}/cancel`
- **Then** the response is `404` with error code `ORDER_NOT_FOUND`, and the other user's
  order is unchanged

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

## Edge cases & errors
- Two cancel requests racing on the same order: exactly one gets `200`, the other `409`
  `ORDER_ALREADY_CANCELLED`.
- Cancelling doesn't change `items` or `total`.

## Test data
- Seeded SKU `TEST-SKU-1` priced at 10.00 (from ORD-001); tests create their own orders.
- Shipped orders: the app has no shipping flow yet, so tests need a test-only way to mark an
  order shipped (see open questions).

## Open questions
- [ ] **How does an order become `shipped`?** Today every order stays `pending` forever, so
      "before it ships" has no defined cutoff. Proposal: add status `shipped` now, plus a
      test-only `POST /test/orders/{id}/ship` that exists only when `SEED_TEST_DATA=true`.
      Is there a real fulfilment flow this should hook into instead?
- [ ] Should a repeat cancel be idempotent (`200`) instead of `409 ORDER_ALREADY_CANCELLED`?
- [ ] Do we need a cancellation reason field, or a time limit (e.g. cancel within N hours)?
- [ ] Should cancelled orders show a timestamp (`cancelled_at`)?
- [ ] Is a confirmation dialog wanted, or should a single click cancel the order?
