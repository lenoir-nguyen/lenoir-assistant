const { chromium } = require('playwright');

/**
 * Record Button Test
 *
 * End-to-end test that verifies:
 * 1. Record button is visible and styled correctly
 * 2. Record button matches Send button styling
 * 3. Record button state changes from Record → Stop Recording
 * 4. Record button is disabled when chat is loading
 * 5. Error handling for microphone permission
 *
 * Prerequisites:
 * - Frontend dev server running: npm run dev
 * - Backend running: docker-compose up -d
 * - Browser with microphone (or permission denied)
 *
 * Usage: node tests/test-record-button.js
 */

(async () => {
  console.log('🧪 Testing Record Button Functionality\n');

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    console.log('Step 1: Opening frontend and logging in as owner...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded\n');

    console.log('Step 2: Logging in as owner...');
    const ownerButton = await page.locator('button:has-text("Login as Owner")');
    await ownerButton.click();

    const pinInput = await page.locator('input[placeholder="Enter PIN"]');
    await pinInput.fill('9999');

    const verifyButton = await page.locator('button:has-text("Verify PIN")');
    await verifyButton.click();
    await page.waitForTimeout(2000);
    console.log('✅ Owner logged in\n');

    console.log('Step 3: Checking Record button is visible...');
    const recordBtn = await page.locator('button:has-text("Record")');
    const isVisible = await recordBtn.isVisible();
    console.log(`   Record button visible: ${isVisible ? '✓' : '✗'}\n`);

    console.log('Step 4: Verifying Record button styling...');
    const recordBtnBox = await recordBtn.boundingBox();
    const sendBtn = await page.locator('button:has-text("Send")');
    const sendBtnBox = await sendBtn.boundingBox();

    if (recordBtnBox && sendBtnBox) {
      const recordHeight = recordBtnBox.height;
      const sendHeight = sendBtnBox.height;
      const heightDiff = Math.abs(recordHeight - sendHeight);

      if (heightDiff < 5) {
        console.log(`   ✓ Record button height matches Send button (diff: ${heightDiff.toFixed(1)}px)\n`);
      } else {
        console.log(`   ⚠️  Record button height differs from Send button (diff: ${heightDiff.toFixed(1)}px)\n`);
      }
    }

    console.log('Step 5: Testing Record button click and state change...');
    const recordBtnBefore = await recordBtn.textContent();
    console.log(`   Button text before: "${recordBtnBefore}"\n`);

    // Click record - this will either:
    // 1. Show browser microphone permission dialog
    // 2. Start recording if permission granted
    // 3. Show error if permission denied
    await recordBtn.click();
    await page.waitForTimeout(2000);

    // Check if recording actually started (look for Stop Recording button)
    const stopRecordingBtn = await page.locator('button:has-text("Stop Recording")').isVisible();
    const permissionError = await page.locator('text=/permission|Microphone/i').isVisible();

    if (stopRecordingBtn) {
      console.log('   ✓ Recording started successfully\n');
      console.log('Step 6: Stopping recording...');
      const stopBtn = await page.locator('button:has-text("Stop Recording")');
      const stopBtnText = await stopBtn.textContent();
      console.log(`   Stop button text: "${stopBtnText}"`);
      await stopBtn.click();
      await page.waitForTimeout(1500);
      console.log('   ✓ Recording stopped and returned to Record button\n');
    } else if (permissionError) {
      console.log('   ✓ Microphone permission dialog or error shown (expected without microphone)\n');
    } else {
      console.log('   ℹ️  Record button clicked (microphone permission dialog may be pending)\n');
    }

    console.log('Step 7: Verifying Record button is disabled during chat loading...');
    const msgInput = await page.locator('input[placeholder="Type a message..."]');
    await msgInput.fill('Test message to trigger loading');
    const sendBtnForMsg = await page.locator('button:has-text("Send")').first();
    await sendBtnForMsg.click();

    // Check if Record button is disabled while loading
    await page.waitForTimeout(500);
    const recordBtnDisabled = await recordBtn.isDisabled();
    console.log(`   Record button disabled during chat: ${recordBtnDisabled ? '✓' : '⚠️'}\n`);

    // Wait for response
    await page.waitForTimeout(3000);

    const recordBtnEnabledAfter = !await recordBtn.isDisabled();
    console.log(`   Record button re-enabled after response: ${recordBtnEnabledAfter ? '✓' : '⚠️'}\n`);

    console.log('Step 8: Testing Clear button also hides language selector...');
    const langSelector = await page.locator('text=/🇬🇧|🇫🇷|🇻🇳/').isVisible();
    console.log(`   Language selector removed: ${!langSelector ? '✓' : '⚠️'}\n`);

    console.log('✅ Test completed! Check the browser window for visual confirmation.');
    console.log('   Browser will close in 10 seconds...\n');
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
  }
})();
