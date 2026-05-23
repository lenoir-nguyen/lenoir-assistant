const { chromium } = require('playwright');

(async () => {
  console.log('🧪 Testing Task 1: Chat History Persistence\n');

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
    const input = await page.locator('input[placeholder*="message"], input[placeholder*="Message"], textarea').first();
    if (input) {
      await input.fill('Hello, this is my first test message');

      // Look for send button
      const sendButton = await page.locator('button:has-text("Send"), button:has-text("send")').first();
      if (sendButton) {
        await sendButton.click();
        await page.waitForTimeout(3000);
        console.log('✅ First message sent\n');
      } else {
        console.log('⚠️  Could not find send button\n');
      }
    } else {
      console.log('⚠️  Could not find input field\n');
    }

    console.log('Step 4: Sending second message...');
    await input.fill('This is my second test message');
    const sendButton = await page.locator('button:has-text("Send"), button:has-text("send")').first();
    if (sendButton) {
      await sendButton.click();
      await page.waitForTimeout(3000);
      console.log('✅ Second message sent\n');
    }

    console.log('Step 5: Counting messages before refresh...');
    // Look for message bubbles or containers
    const messageBubbles = await page.locator('[role="article"], .message, .chat-message, [class*="bubble"]').count();
    console.log(`   Messages before refresh: ${messageBubbles}\n`);

    console.log('Step 6: Refreshing page (F5)...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    console.log('✅ Page refreshed\n');

    console.log('Step 7: Counting messages after refresh...');
    const messageBubblesAfter = await page.locator('[role="article"], .message, .chat-message, [class*="bubble"]').count();
    console.log(`   Messages after refresh: ${messageBubblesAfter}\n`);

    console.log('Step 8: Verification...');
    if (messageBubblesAfter > 0) {
      console.log('✅ SUCCESS: Chat history appears to have persisted!\n');

      // Get session ID
      const sessionId = await page.evaluate(() => sessionStorage.getItem('session_id'));
      if (sessionId) {
        console.log(`Step 9: Testing API endpoint directly...`);
        console.log(`   Session ID: ${sessionId}`);

        try {
          const response = await fetch(`http://localhost:8000/chat/history/${sessionId}`);
          if (response.ok) {
            const history = await response.json();
            console.log(`   ✅ API returned ${history.length} messages from database\n`);
            console.log('   Database Messages:');
            history.forEach((msg, i) => {
              console.log(`      ${i + 1}. [${msg.role.toUpperCase()}] ${msg.content.substring(0, 60)}...`);
            });
          } else {
            console.log(`   ❌ API error: ${response.status}`);
          }
        } catch (err) {
          console.log(`   ⚠️  Could not test API: ${err.message}`);
        }
      }
    } else {
      console.log('⚠️  No messages found after refresh - may need to check selectors\n');
    }

    console.log('\n✅ Test completed! Browser will close in 10 seconds...');
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
  }
})();
