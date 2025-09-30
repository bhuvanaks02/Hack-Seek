import { test, expect } from '@playwright/test';

test.describe('AI Recommendations', () => {
  test('should show recommendations page', async ({ page }) => {
    await page.goto('/recommendations');

    await expect(page.locator('h1')).toContainText('AI Recommendations');
    await expect(page.locator('text=Personalized hackathon suggestions')).toBeVisible();
  });

  test('should show sign in prompt when not authenticated', async ({ page }) => {
    await page.goto('/recommendations');

    // Should show sign in message
    await expect(page.locator('text=Sign in required')).toBeVisible();
    await expect(page.locator('button', { hasText: 'Sign In' })).toBeVisible();
  });

  test('should display how AI works section', async ({ page }) => {
    await page.goto('/recommendations');

    await expect(page.locator('text=How AI Recommendations Work')).toBeVisible();
    await expect(page.locator('text=We analyze your skills')).toBeVisible();
  });

  test('should show improvement tips', async ({ page }) => {
    await page.goto('/recommendations');

    await expect(page.locator('text=Improve Your Recommendations')).toBeVisible();
    await expect(page.locator('text=Complete your profile')).toBeVisible();
  });
});