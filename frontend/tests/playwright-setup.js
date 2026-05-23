const { chromium } = require('playwright');

/**
 * Playwright Setup Verification Test
 *
 * Verifies that Playwright is properly installed and configured
 * by opening a real website (Google) and checking the page title.
 *
 * Usage: node tests/playwright-setup.js
 */

(async () => {
  console.log('Testing Playwright setup by opening Google...\n');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('Opening www.google.com...');
    await page.goto('https://www.google.com', { waitUntil: 'networkidle' });

    const title = await page.title();
    console.log(`✅ Success! Page title: ${title}`);
    console.log('✅ Playwright is properly configured!\n');

  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();
