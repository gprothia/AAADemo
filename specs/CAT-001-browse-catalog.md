---
id: CAT-001
title: Browse the product catalog
status: implemented
owner: "@gprothia"
issue: "#2"
ui_routes: ["/products"]
---

# CAT-001: Browse the product catalog

## Why
Customers need to see what they can buy, and at what price, before placing an order.

## Scope
- In: listing all products; looking up one product by SKU; a catalog page.
- Out: search, filtering, images, stock levels.

## Acceptance criteria

### CAT-001-AC1 [api]
- **Given** the seeded catalog
- **When** the client sends `GET /products`
- **Then** the response is `200` with a list where every product has `sku`, `name` and `price`,
  and it includes `TEST-SKU-1` priced at `10.00`

### CAT-001-AC2 [api]
- **Given** a SKU that does not exist
- **When** the client sends `GET /products/{sku}`
- **Then** the response is `404` with code `SKU_NOT_FOUND`

### CAT-001-AC3 [ui]
- **Given** a user on `/products`
- **Then** they see a table with one row per product showing its name and its price
  formatted as dollars (e.g. "Blue Mug" — "$10.00")

## Test data
Seeded products: `TEST-SKU-1` Blue Mug $10.00, `TEST-SKU-2` Notebook $4.50,
`TEST-SKU-3` Desk Lamp $32.00.
