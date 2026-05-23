const { chromium } = require('playwright');

/**
 * Localhost Frontend Test
 *
 * Opens the frontend application at localhost:3000 in a visible browser
 * and keeps it open for 30 seconds for manual inspection.
 *
 * Prerequisites:
 * - Frontend dev server running: npm run dev
 * - Backend running: docker-compose up -d
 *
 * Usage: node tests/test-localhost.js
 */

(async () => {
  console.log('🧪 Testing localhost with visible browser...\n');

  // Launch browser WITH visible window (headless: false)
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    console.log('Opening http://localhost:3000 in visible Chrome window...');
    console.log('(A Chrome window should appear - please wait...)\n');

    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 10000 });

    const title = await page.title();
    console.log(`✅ Frontend loaded! Page title: ${title}`);
    console.log('✅ Browser window should be visible now!\n');

    // Keep browser open for 30 seconds so you can interact with it
    console.log('Browser will stay open for 30 seconds...');
    console.log('You can interact with it, or I\'ll close it automatically.\n');

    await page.waitForTimeout(30000);

  } catch (error) {
    console.error('❌ Error:', error.message);
    console.log('\nMake sure:');
    console.log('  1. Frontend dev server is running (npm run dev on port 3000)');
    console.log('  2. Backend is running (docker-compose up -d)');
  } finally {
    await browser.close();
    console.log('\n✅ Browser closed');
  }
})();
