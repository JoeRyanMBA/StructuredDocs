const { test, expect } = require('@playwright/test');

test.describe('Login Page Audit', () => {
  test.setTimeout(60000);

  test('should load the login page and allow user to log in', async ({ page }) => {
    await page.goto('https://structureddocs.joe-ryan.mba/login');

    // Wait for the h1 to be visible, which indicates the page is loaded
    await expect(page.locator('h1')).toBeVisible();

    await page.fill('input[name="email"]', 'admin@example.com');
    await page.fill('input[name="password"]', 'ChangeMe123!');
    await page.click('button[type="submit"]');

    // Wait for the URL to change to the dashboard
    await page.waitForURL('https://structureddocs.joe-ryan.mba/');
    await expect(page).toHaveTitle(/Structured Docs/);
    await expect(page.locator('h1')).toContainText('Start');
  });
});
