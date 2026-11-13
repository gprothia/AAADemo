"""Example API tests generated from specs/ORD-001-create-order.md."""
import pytest

SKU = "TEST-SKU-1"  # seeded at 10.00


@pytest.mark.ac("ORD-001-AC1")
def test_creates_pending_order_with_correct_total(api):
    r = api.post("/orders", json={"items": [{"sku": SKU, "quantity": 2}]})
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert body["status"] == "pending"
    assert body["total"] == pytest.approx(20.00)


@pytest.mark.ac("ORD-001-AC2")
def test_rejects_zero_quantity(api):
    r = api.post("/orders", json={"items": [{"sku": SKU, "quantity": 0}]})
    assert r.status_code == 422
    assert "items[0].quantity" in r.text


@pytest.mark.ac("ORD-001-AC3")
def test_rejects_more_than_50_line_items(api):
    items = [{"sku": SKU, "quantity": 1}] * 51
    r = api.post("/orders", json={"items": items})
    assert r.status_code == 422
    assert r.json()["code"] == "TOO_MANY_ITEMS"
