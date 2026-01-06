import { test, expect } from '@playwright/test';

/**
 * Basic App Tests
 * Tests that verify the application loads and displays correctly.
 */

test.describe('App Loading', () => {
    test('should load the home page', async ({ page }) => {
        await page.goto('/');

        // Check that the page loads (no error page)
        await expect(page).not.toHaveTitle(/error/i);

        // Wait for the app to hydrate
        await page.waitForLoadState('networkidle');
    });

    test('should have proper page title', async ({ page }) => {
        await page.goto('/');

        // Check for a reasonable title
        const title = await page.title();
        expect(title.length).toBeGreaterThan(0);
    });

    test('should be responsive on mobile viewport', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');

        // Page should still load correctly
        await page.waitForLoadState('networkidle');
        await expect(page).not.toHaveTitle(/error/i);
    });
});
