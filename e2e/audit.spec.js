const { test, expect } = require('@playwright/test');

test.describe('StructuredDocs UAT Audit', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://structureddocs.joe-ryan.mba/login');
    // Wait for the login form to be visible
    await expect(page.locator('form')).toBeVisible({ timeout: 60000 });
    await page.screenshot({ path: 'test-results/login-page.png' });
    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'ChangeMe123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('https://structureddocs.joe-ryan.mba/');
  });

  test('should login and redirect to dashboard', async ({ page }) => {
    await expect(page).toHaveTitle(/Structured Docs/);
    await expect(page.locator('h1')).toContainText('Start');
  });
});
