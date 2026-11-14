"""API tests generated from specs/ORD-002-cancel-order.md."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

SKU = "TEST-SKU-1"  # seeded at 10.00
OWNER = {"X-User": "ord002-owner"}

# Test runner and API may run on different machines (GKE sandbox); allow small clock skew.
CLOCK_SKEW = timedelta(seconds=2)


def create_order(api, headers=OWNER):
    r = api.post("/orders", json={"items": [{"sku": SKU, "quantity": 2}]}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def cancel(api, order_id, headers=OWNER):
    return api.post(f"/orders/{order_id}/cancel", headers=headers)


@pytest.mark.ac("ORD-002-AC1")
def test_owner_cancels_pending_order(api):
    order = create_order(api)

    r = cancel(api, order["id"])

    assert r.status_code == 200
    assert r.json()["id"] == order["id"]
    assert r.json()["status"] == "cancelled"
    assert api.get(f"/orders/{order['id']}", headers=OWNER).json()["status"] == "cancelled"


@pytest.mark.ac("ORD-002-AC1")
def test_cancel_keeps_items_and_total(api):
    order = create_order(api)

    body = cancel(api, order["id"]).json()

    assert body["items"] == order["items"]
    assert body["total"] == pytest.approx(order["total"])


@pytest.mark.ac("ORD-002-AC2")
def test_cannot_cancel_shipped_order(api):
    order = create_order(api)
    ship = api.post(f"/test/orders/{order['id']}/ship")
    assert ship.status_code == 200, ship.text

    r = cancel(api, order["id"])

    assert r.status_code == 409
    assert r.json()["code"] == "ORDER_ALREADY_SHIPPED"
    assert api.get(f"/orders/{order['id']}", headers=OWNER).json()["status"] == "shipped"


@pytest.mark.ac("ORD-002-AC3")
def test_cannot_cancel_twice(api):
    order = create_order(api)
    assert cancel(api, order["id"]).status_code == 200

    r = cancel(api, order["id"])

    assert r.status_code == 409
    assert r.json()["code"] == "ORDER_ALREADY_CANCELLED"


@pytest.mark.ac("ORD-002-AC3")
def test_concurrent_cancels_one_wins(api):
    order = create_order(api)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: cancel(api, order["id"]), range(2)))

    statuses = sorted(r.status_code for r in responses)
    assert statuses == [200, 409]
    loser = next(r for r in responses if r.status_code == 409)
    assert loser.json()["code"] == "ORDER_ALREADY_CANCELLED"


@pytest.mark.ac("ORD-002-AC4")
def test_cannot_cancel_other_users_order(api):
    order = create_order(api)

    r = cancel(api, order["id"], headers={"X-User": "ord002-someone-else"})

    assert r.status_code == 404
    assert r.json()["code"] == "ORDER_NOT_FOUND"
    assert api.get(f"/orders/{order['id']}", headers=OWNER).json()["status"] == "pending"


@pytest.mark.ac("ORD-002-AC4")
def test_cancel_unknown_order_returns_404(api):
    r = cancel(api, "no-such-order")

    assert r.status_code == 404
    assert r.json()["code"] == "ORDER_NOT_FOUND"


@pytest.mark.ac("ORD-002-AC8")
def test_cancel_records_cancelled_at(api):
    order = create_order(api)
    assert api.get(f"/orders/{order['id']}", headers=OWNER).json()["cancelled_at"] is None

    sent = datetime.now(timezone.utc)
    r = cancel(api, order["id"])
    arrived = datetime.now(timezone.utc)

    assert r.status_code == 200
    raw = r.json()["cancelled_at"]
    assert raw.endswith("Z") or raw.endswith("+00:00"), f"not UTC: {raw}"
    cancelled_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    assert sent - CLOCK_SKEW <= cancelled_at <= arrived + CLOCK_SKEW
