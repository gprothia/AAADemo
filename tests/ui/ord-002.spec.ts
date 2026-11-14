// UI tests generated from specs/ORD-002-cancel-order.md
import { test, expect, APIRequestContext } from '@playwright/test';

const API = process.env.API_BASE_URL ?? 'http://localhost:8080';
const USER = { 'X-User': 'demo' }; // the web app's signed-in user

async function createOrder(request: APIRequestContext): Promise<string> {
  const r = await request.post(`${API}/orders`, {
    headers: USER,
    data: { items: [{ sku: 'TEST-SKU-1', quantity: 1 }] },
  });
  expect(r.status()).toBe(201);
  return (await r.json()).id;
}

test('cancels a pending order after confirming', { tag: '@ORD-002-AC5' }, async ({ page, request }) => {
  const id = await createOrder(request);
  await page.goto(`/orders/${id}`);

  await page.getByRole('button', { name: 'Cancel order' }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Yes, cancel order' }).click();

  await expect(page.getByRole('heading', { name: 'Order cancelled' })).toBeVisible();
  await expect(page.getByTestId('status-badge')).toHaveText('Cancelled');
  await expect(page.getByRole('button', { name: 'Cancel order' })).toHaveCount(0);
});

test('keeps the order when cancel is dismissed', { tag: '@ORD-002-AC6' }, async ({ page, request }) => {
  const id = await createOrder(request);
  await page.goto(`/orders/${id}`);

  await page.getByRole('button', { name: 'Cancel order' }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Keep order' }).click();

  await expect(page.getByRole('dialog')).toBeHidden();
  await expect(page.getByRole('heading', { name: 'Order received' })).toBeVisible();
  await expect(page.getByTestId('status-badge')).toHaveText('Pending');
});

test('no cancel button on a shipped order', { tag: '@ORD-002-AC7' }, async ({ page, request }) => {
  const id = await createOrder(request);
  expect((await request.post(`${API}/test/orders/${id}/ship`)).status()).toBe(200);

  await page.goto(`/orders/${id}`);

  await expect(page.getByTestId('status-badge')).toHaveText('Shipped');
  await expect(page.getByRole('button', { name: 'Cancel order' })).toHaveCount(0);
});

test('no cancel button on a cancelled order', { tag: '@ORD-002-AC7' }, async ({ page, request }) => {
  const id = await createOrder(request);
  expect((await request.post(`${API}/orders/${id}/cancel`, { headers: USER })).status()).toBe(200);

  await page.goto(`/orders/${id}`);

  await expect(page.getByTestId('status-badge')).toHaveText('Cancelled');
  await expect(page.getByRole('button', { name: 'Cancel order' })).toHaveCount(0);
});
