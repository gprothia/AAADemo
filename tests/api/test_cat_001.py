"""API tests generated from specs/CAT-001-browse-catalog.md."""
import pytest


@pytest.mark.ac("CAT-001-AC1")
def test_lists_products_with_sku_name_and_price(api):
    r = api.get("/products")
    assert r.status_code == 200
    products = r.json()
    assert products, "catalog should not be empty"
    for p in products:
        assert {"sku", "name", "price"} <= p.keys()
    mug = next(p for p in products if p["sku"] == "TEST-SKU-1")
    assert mug["price"] == pytest.approx(10.00)


@pytest.mark.ac("CAT-001-AC2")
def test_unknown_sku_returns_404(api):
    r = api.get("/products/NO-SUCH-SKU")
    assert r.status_code == 404
    assert r.json()["code"] == "SKU_NOT_FOUND"
