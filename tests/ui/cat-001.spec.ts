// UI tests generated from specs/CAT-001-browse-catalog.md
import { test, expect } from '@playwright/test';

test('catalog page lists products with dollar prices', { tag: '@CAT-001-AC3' }, async ({ page }) => {
  await page.goto('/products');
  const table = page.getByRole('table', { name: 'Products' });
  await expect(table).toBeVisible();

  const mug = table.getByRole('row').filter({ hasText: 'Blue Mug' });
  await expect(mug).toHaveCount(1);
  await expect(mug).toContainText('$10.00');

  // one header row + one row per seeded product
  await expect(table.getByRole('row')).toHaveCount(4);
});
