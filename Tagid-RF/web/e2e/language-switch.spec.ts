import { test, expect } from '@playwright/test';

test.describe('Language and Directionality', () => {
    test.slow(); // Mark test as slow to increase timeout

    test('should switch language and layout direction correctly', async ({ page }) => {
        // 1. Go to Login Page
        await page.goto('/');

        // 2. Login as Network Admin 
        // Click role card (using regex for robustness)
        const networkAdminRole = page.getByRole('button', { name: /מנהל רשת/i });
        await networkAdminRole.click();

        // Click connect button
        const loginButton = page.getByRole('button', { name: /התחבר/i });
        await loginButton.click();

        // 3. Wait for Dashboard to load and verify we are in
        await page.waitForURL('**/dashboard');

        // 4. Navigate to Settings
        await page.goto('/settings');

        // 5. Initial State (Hebrew/RTL)
        // Verify HTML dir is RTL
        await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
        // Verify page title is in Hebrew
        await expect(page.getByRole('heading', { name: 'הגדרות' })).toBeVisible();

        // 6. Switch to English
        // The language select is in the first setting row.
        // It's a select element with options 'he' and 'en'
        const langSelect = page.locator('select').first();
        await langSelect.selectOption('en');

        // Allow a brief moment for state update if needed, though expect should retry

        // 7. Verify English State (LTR)
        // Verify HTML dir is LTR
        await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');

        // Verify English text for Heading
        await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

        // Verify English text for Sections
        await expect(page.getByText('General Settings')).toBeVisible();
        await expect(page.getByText('Network Details')).toBeVisible();

        // Verify Sidebar Navigation is English
        // "General" is a link in the sidebar
        await expect(page.getByRole('link', { name: 'General' })).toBeVisible();

        // 8. Switch back to Hebrew
        await langSelect.selectOption('he');

        // 9. Verify Hebrew State again
        await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
        await expect(page.getByRole('heading', { name: 'הגדרות' })).toBeVisible();
    });
});
