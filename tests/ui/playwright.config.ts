import { defineConfig, devices } from '@playwright/test';

const out = process.env.REPORT_DIR ?? 'reports';

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ['list'],
    ['junit', { outputFile: `${out}/ui-junit.xml` }],
    ['html', { outputFolder: `${out}/ui-html`, open: 'never' }],
  ],
  use: {
    baseURL: process.env.WEB_BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
