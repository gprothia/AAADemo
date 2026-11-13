"""Storefront web app: the UI half of the 'existing app'.

Pages:
  /products         CAT-001  catalog table
  /orders/new       ORD-001  build and place an order
  /orders/{id}      ORD-001  order confirmation

Browser calls go to /api/* on this server, which forwards them to the API service,
so the browser only ever talks to one host.
"""
from __future__ import annotations

import html
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

API_URL = os.environ.get("API_URL", "http://localhost:8080")
USER = "demo"  # stand-in for a signed-in user

app = FastAPI(title="Storefront")
client = httpx.AsyncClient(base_url=API_URL, timeout=10)

CSS = """
body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;color:#1f2328}
nav a{margin-right:16px}
table{border-collapse:collapse;width:100%;margin:16px 0}
th,td{text-align:left;padding:8px;border-bottom:1px solid #d0d7de}
button{padding:8px 14px;border-radius:6px;border:1px solid #1f6feb;background:#1f6feb;color:#fff;cursor:pointer}
button:disabled{background:#8c959f;border-color:#8c959f;cursor:not-allowed}
button.secondary{background:#fff;color:#1f6feb}
.row{display:flex;gap:12px;align-items:end;margin:8px 0}
label{display:flex;flex-direction:column;font-size:13px;gap:4px}
input{padding:6px;border:1px solid #d0d7de;border-radius:6px}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;background:#ddf4ff;color:#0969da;font-size:13px}
.error{color:#cf222e}
"""


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>{CSS}</style></head><body>
<nav><a href="/products">Products</a><a href="/orders/new">New order</a></nav>
{body}</body></html>"""
    )


def money(v: float) -> str:
    return f"${v:,.2f}"


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/")
def home():
    return RedirectResponse("/products")


# ---------------------------------------------------------------- CAT-001


@app.get("/products")
async def products():
    items = (await client.get("/products")).json()
    rows = "".join(
        f"<tr><td>{html.escape(p['name'])}</td><td>{html.escape(p['sku'])}</td><td>{money(p['price'])}</td></tr>"
        for p in items
    )
    return page(
        "Products",
        f"""<h1>Products</h1>
<table aria-label="Products"><thead><tr><th>Name</th><th>SKU</th><th>Price</th></tr></thead>
<tbody>{rows}</tbody></table>""",
    )


# ---------------------------------------------------------------- ORD-001


@app.get("/orders/new")
def new_order():
    return page(
        "New order",
        """<h1>New order</h1>
<div id="lines"></div>
<div class="row">
  <button type="button" class="secondary" id="add">Add item</button>
  <button type="button" id="place" disabled>Place order</button>
</div>
<p class="error" id="err" role="alert"></p>
<script>
const lines = document.getElementById('lines');
const place = document.getElementById('place');
let n = 0;
function refresh(){ place.disabled = lines.children.length === 0; }
document.getElementById('add').onclick = () => {
  n += 1;
  const row = document.createElement('div');
  row.className = 'row';
  row.innerHTML = `<label>SKU<input name="sku" id="sku-${n}"></label>
                   <label>Quantity<input name="quantity" type="number" min="1" value="1" id="qty-${n}"></label>`;
  lines.appendChild(row); refresh();
};
place.onclick = async () => {
  const items = [...lines.children].map(r => ({
    sku: r.querySelector('[name=sku]').value.trim(),
    quantity: Number(r.querySelector('[name=quantity]').value)
  }));
  const res = await fetch('/api/orders', {method:'POST', headers:{'Content-Type':'application/json'},
                                         body: JSON.stringify({items})});
  const body = await res.json();
  if (res.status === 201) { location.href = '/orders/' + body.id; }
  else { document.getElementById('err').textContent = body.message || 'Could not place order'; }
};
refresh();
</script>""",
    )


@app.get("/orders/{order_id}")
async def show_order(order_id: str):
    r = await client.get(f"/orders/{order_id}", headers={"X-User": USER})
    if r.status_code != 200:
        return page("Not found", "<h1>Order not found</h1>")
    o = r.json()
    rows = "".join(
        f"<tr><td>{html.escape(i['sku'])}</td><td>{i['quantity']}</td><td>{money(i['line_total'])}</td></tr>"
        for i in o["items"]
    )
    headline = "Order received" if o["status"] == "pending" else f"Order {html.escape(o['status'])}"
    return page(
        f"Order {o['id']}",
        f"""<h1>{headline}</h1>
<p>Order <code>{o['id']}</code> <span class="badge" data-testid="status-badge">{html.escape(o['status'].capitalize())}</span></p>
<table aria-label="Order items"><thead><tr><th>SKU</th><th>Qty</th><th>Line total</th></tr></thead>
<tbody>{rows}</tbody></table>
<p>Total: <strong data-testid="order-total">{money(o['total'])}</strong></p>""",
    )


# ---------------------------------------------------------------- API pass-through


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request):
    r = await client.request(
        request.method,
        f"/{path}",
        content=await request.body(),
        headers={"Content-Type": request.headers.get("content-type", "application/json"), "X-User": USER},
    )
    return Response(r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
