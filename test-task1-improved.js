const { chromium } = require('playwright');

(async () => {
  console.log('🧪 Testing Task 1: Chat History Persistence (Improved)\n');

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    console.log('Step 1: Opening frontend at http://localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded\n');

    console.log('Step 2: Setting owner token in sessionStorage...');
    await page.evaluate(() => {
      sessionStorage.setItem('auth_token', 'test-token');
    });
    await page.reload({ waitUntil: 'networkidle' });
    console.log('✅ Owner token set\n');

    console.log('Step 3: Sending first message...');
    const input = await page.locator('input[placeholder="Type a message..."]');
    await input.fill('Hello! This is task 1 test message 1');

    const sendBtn = await page.locator('button:has-text("Send")');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ First message sent\n');

    console.log('Step 4: Sending second message...');
    await input.fill('This is task 1 test message 2');
    await sendBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ Second message sent\n');

    // Wait for messages to render
    await page.waitForTimeout(1000);

    console.log('Step 5: Getting message count before refresh...');
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

    console.log('Step 6: Refreshing page (F5)...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    console.log('✅ Page refreshed\n');

    console.log('Step 7: Getting message count after refresh...');
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

    console.log('Step 8: Verification...');
    if (messagesAfter >= messagesBefore && messagesAfter > 0) {
      console.log(`✅ SUCCESS: Chat history persisted!`);
      console.log(`   Before refresh: ${messagesBefore} messages`);
      console.log(`   After refresh: ${messagesAfter} messages\n`);
    } else if (messagesAfter > 0) {
      console.log(`⚠️  Messages found after refresh but count decreased`);
      console.log(`   Before: ${messagesBefore}, After: ${messagesAfter}\n`);
    } else {
      console.log(`⚠️  No messages found after refresh\n`);
    }

    // Test API endpoint
    console.log('Step 9: Testing /chat/history API endpoint...');
    const sessionId = await page.evaluate(() => sessionStorage.getItem('session_id'));

    if (sessionId) {
      console.log(`   Session ID: ${sessionId}`);
      try {
        const response = await fetch(`http://localhost:8000/chat/history/${sessionId}`);
        if (response.ok) {
          const history = await response.json();
          console.log(`   ✅ API returned ${history.length} messages from PostgreSQL\n`);
          console.log('   Database Messages:');
          history.forEach((msg, i) => {
            console.log(`      ${i + 1}. [${msg.role.toUpperCase()}] "${msg.content.substring(0, 50)}..."`);
          });
          console.log();
        } else {
          console.log(`   ❌ API error: ${response.status}\n`);
        }
      } catch (err) {
        console.log(`   ⚠️  Could not reach API: ${err.message}\n`);
      }
    } else {
      console.log(`   ⚠️  No session ID found\n`);
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
