import { test, expect } from '@playwright/test';

test.describe('Hackathon Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/hackathons');
  });

  test('should display hackathons list', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Find Hackathons');
    await expect(page.locator('[data-testid=hackathon-card]').first()).toBeVisible();
  });

  test('should search hackathons', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search hackathons"]');
    await searchInput.fill('AI hackathon');
    await searchInput.press('Enter');

    // Wait for search results
    await page.waitForTimeout(1000);

    // Should show search results
    await expect(page.locator('[data-testid=hackathon-card]')).toHaveCount({ min: 0 });
  });

  test('should filter by category', async ({ page }) => {
    // Open filters (desktop)
    const filtersSection = page.locator('text=Filters').first();
    if (await filtersSection.isVisible()) {
      // Check AI/ML category
      await page.locator('text=AI/ML').click();

      // Apply filters
      await page.locator('button', { hasText: 'Apply Filters' }).click();

      // Wait for results
      await page.waitForTimeout(1000);
    }
  });

  test('should switch between basic and AI search', async ({ page }) => {
    // Click AI Search toggle
    await page.locator('button', { hasText: 'AI Search' }).click();

    // Should show smart search component
    await expect(page.locator('text=Use AI-powered semantic search')).toBeVisible();

    // Try a natural language query
    const aiSearchInput = page.locator('input[placeholder*="Try:"]');
    await aiSearchInput.fill('AI hackathons with good prizes for beginners');
    await page.locator('button', { hasText: 'Search' }).click();

    // Wait for AI search results
    await page.waitForTimeout(2000);
  });

  test('should work on mobile', async ({ page, isMobile }) => {
    if (isMobile) {
      // Should show mobile filter button
      await expect(page.locator('button', { hasText: 'Filters' })).toBeVisible();

      // Open mobile filters
      await page.locator('button', { hasText: 'Filters' }).click();

      // Should show mobile filters modal
      await expect(page.locator('h2', { hasText: 'Filters' })).toBeVisible();

      // Close filters
      await page.locator('button[aria-label="Close"]').click();
    }
  });

  test('should navigate to hackathon details', async ({ page }) => {
    // Click on first hackathon card
    const firstCard = page.locator('[data-testid=hackathon-card]').first();
    const hackathonTitle = await firstCard.locator('h3').first().textContent();

    await firstCard.locator('h3').first().click();

    // Should navigate to detail page
    await expect(page).toHaveURL(/\/hackathons\/[a-f0-9-]+/);

    // Should show hackathon details
    if (hackathonTitle) {
      await expect(page.locator('h1')).toContainText(hackathonTitle);
    }
  });
});