// Example UI tests generated from specs/ORD-001-create-order.md
import { test, expect } from '@playwright/test';

test('places an order and shows confirmation', { tag: '@ORD-001-AC4' }, async ({ page }) => {
  await page.goto('/orders/new');
  await page.getByRole('button', { name: 'Add item' }).click();
  await page.getByLabel('SKU').fill('TEST-SKU-1');
  await page.getByLabel('Quantity').fill('2');
  await page.getByRole('button', { name: 'Place order' }).click();

  await expect(page).toHaveURL(/\/orders\/[\w-]+$/);
  await expect(page.getByText('Order received')).toBeVisible();
  await expect(page.getByTestId('order-total')).toHaveText('$20.00');
});

test('place order is disabled with no items', { tag: '@ORD-001-AC5' }, async ({ page }) => {
  await page.goto('/orders/new');
  await expect(page.getByRole('button', { name: 'Place order' })).toBeDisabled();
});
