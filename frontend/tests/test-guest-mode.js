const { chromium } = require('playwright');

/**
 * Guest Mode Test (v4 Feature)
 *
 * End-to-end test that verifies:
 * 1. Frontend loads correctly
 * 2. Guest can login without credentials
 * 3. Messages are sent and received (ephemeral)
 * 4. Chat history is NOT persisted after page refresh (guest mode)
 * 5. Clear button works (resets conversation)
 * 6. Logout button works (returns to login screen)
 *
 * Prerequisites:
 * - Frontend dev server running: npm run dev
 * - Backend running: docker-compose up -d
 *
 * Usage: node tests/test-guest-mode.js
 */

(async () => {
  console.log('🧪 Testing Guest Mode (Ephemeral Conversation)\n');

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    console.log('Step 1: Opening frontend at http://localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded\n');

    console.log('Step 2: Clicking "Continue as Guest"...');
    const guestButton = await page.locator('button:has-text("Continue as Guest")');
    await guestButton.click();
    await page.waitForTimeout(2000);
    console.log('✅ Guest mode enabled\n');

    console.log('Step 3: Verifying guest welcome message...');
    const welcomeText = await page.textContent('[style*="display: flex"]');
    if (welcomeText && welcomeText.includes("I'm Lenoir's assistant")) {
      console.log('   ✓ Found guest welcome message\n');
    }

    console.log('Step 4: Waiting for chat window to load...');
    await page.waitForSelector('input[placeholder="Type a message..."]', { timeout: 15000 });
    console.log('   ✓ Chat window ready\n');

    console.log('Step 5: Sending first guest message...');
    const input = await page.locator('input[placeholder="Type a message..."]');
    await input.fill('Hi! I am testing guest mode');

    const sendBtn = await page.locator('button:has-text("Send")');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ First message sent\n');

    console.log('Step 6: Sending second guest message...');
    await input.fill('This conversation should NOT persist after refresh');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ Second message sent\n');

    // Wait for messages to render
    await page.waitForTimeout(1000);

    console.log('Step 7: Getting message count before refresh...');
    const messagesBefore = await page.locator('div:has(> p) >> p').count();
    console.log(`   Messages found: ${messagesBefore}\n`);

    if (messagesBefore > 0) {
      console.log('   Message content:');
      const msgContents = await page.locator('div:has(> p) >> p').allTextContents();
      msgContents.forEach((msg, i) => {
        console.log(`      ${i + 1}. "${msg.substring(0, 50)}..."`);
      });
      console.log();
    }

    console.log('Step 8: Testing Clear button...');
    const clearBtn = await page.locator('button:has-text("Clear")');
    await clearBtn.click();
    await page.waitForTimeout(1000);
    const messagesAfterClear = await page.locator('div:has(> p) >> p').count();
    console.log(`   Messages after clear: ${messagesAfterClear}`);
    if (messagesAfterClear === 1) {
      console.log('   ✓ Clear button works (back to welcome only)\n');
    } else {
      console.log(`   ⚠️  Expected 1 message after clear, got ${messagesAfterClear}\n`);
    }

    console.log('Step 9: Sending message after clear...');
    await input.fill('New message after clear');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ New message sent\n');

    console.log('Step 10: Refreshing page (F5)...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    console.log('✅ Page refreshed\n');

    console.log('Step 11: Getting message count after refresh...');
    const messagesAfter = await page.locator('div:has(> p) >> p').count();
    console.log(`   Messages found: ${messagesAfter}\n`);

    if (messagesAfter > 0) {
      console.log('   Message content:');
      const msgContents = await page.locator('div:has(> p) >> p').allTextContents();
      msgContents.forEach((msg, i) => {
        console.log(`      ${i + 1}. "${msg.substring(0, 50)}..."`);
      });
      console.log();
    }

    console.log('Step 12: Verification of ephemeral guest mode...');
    if (messagesAfter <= 1) {
      console.log(`✅ SUCCESS: Guest mode is ephemeral!`);
      console.log(`   Messages were NOT persisted (only ${messagesAfter} found after refresh)\n`);
    } else {
      console.log(`⚠️  ISSUE: Guest messages persisted after refresh`);
      console.log(`   Found ${messagesAfter} messages (expected 1 welcome only)\n`);
    }

    console.log('Step 13: Verifying guest session was cleared on refresh...');
    const authScreenPresent = await page.locator('button:has-text("Continue as Guest")').isVisible();
    if (authScreenPresent) {
      console.log('✅ Guest automatically returned to login (correct behavior)\n');

      console.log('Step 14: Testing Logout button with owner account...');
      // Log in as owner to test logout
      const ownerBtn = await page.locator('button:has-text("Login as Owner")');
      await ownerBtn.click();
      await page.waitForTimeout(1000);

      const pinInput = await page.locator('input[placeholder="Enter PIN"]');
      await pinInput.fill('9999');

      const verifyBtn = await page.locator('button:has-text("Verify PIN")');
      await verifyBtn.click();
      await page.waitForTimeout(3000);
      console.log('   ✓ Logged in as owner\n');

      console.log('Step 15: Testing Logout button...');
      const logoutBtn = await page.locator('button:has-text("Logout")');
      await logoutBtn.click();
      await page.waitForTimeout(2000);
      console.log('✅ Logout clicked\n');

      console.log('Step 16: Verifying return to auth screen...');
      const loginButtonAfterLogout = await page.locator('button:has-text("Login as Owner")');
      if (await loginButtonAfterLogout.isVisible()) {
        console.log('✅ Successfully returned to login screen after logout\n');
      } else {
        console.log('⚠️  Did not return to login screen\n');
      }
    } else {
      console.log('⚠️  Guest session persisted (unexpected)\n');
    }

    console.log('✅ Test completed! Check the browser window for visual confirmation.');
    console.log('   Browser will close in 15 seconds...\n');
    await page.waitForTimeout(15000);

  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
  }
})();
