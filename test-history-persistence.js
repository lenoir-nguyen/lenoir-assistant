const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('🧪 Testing Chat History Persistence (Task 1)\n');

    // Step 1: Navigate to frontend
    console.log('Step 1: Opening frontend at http://localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    console.log('✅ Frontend loaded\n');

    // Step 2: Set auth token in sessionStorage
    console.log('Step 2: Logging in as owner with test token...');
    await page.evaluate(() => {
      sessionStorage.setItem('auth_token', 'test-token');
    });
    await page.reload({ waitUntil: 'networkidle' });
    console.log('✅ Owner token set\n');

    // Step 3: Send first message
    console.log('Step 3: Sending first message...');
    const inputField = await page.locator('input[type="text"]').first();
    await inputField.fill('Hello, this is test message 1');
    await page.locator('button:has-text("Send")').click();
    await page.waitForTimeout(2000); // Wait for response
    console.log('✅ First message sent\n');

    // Step 4: Send second message
    console.log('Step 4: Sending second message...');
    await inputField.fill('This is test message 2');
    await page.locator('button:has-text("Send")').click();
    await page.waitForTimeout(2000); // Wait for response
    console.log('✅ Second message sent\n');

    // Step 5: Count messages before refresh
    const messagesBefore = await page.locator('[role="article"]').count();
    console.log(`Step 5: Messages in chat before refresh: ${messagesBefore}`);

    // Step 6: Refresh page
    console.log('Step 6: Refreshing page (F5)...');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000); // Wait for history to load
    console.log('✅ Page refreshed\n');

    // Step 7: Count messages after refresh
    const messagesAfter = await page.locator('[role="article"]').count();
    console.log(`Step 7: Messages in chat after refresh: ${messagesAfter}`);

    // Step 8: Verify messages persisted
    console.log('\nStep 8: Verification...');
    if (messagesAfter >= messagesBefore - 1) {
      console.log('✅ SUCCESS: Chat history persisted after page refresh!');
      console.log(`   Before refresh: ${messagesBefore} messages`);
      console.log(`   After refresh: ${messagesAfter} messages`);

      // Get all message content
      const messages = await page.locator('[role="article"]').allTextContents();
      console.log('\n📝 Chat Messages:');
      messages.forEach((msg, i) => {
        console.log(`   ${i + 1}. ${msg.substring(0, 50)}...`);
      });
    } else {
      console.log('❌ FAILED: Chat history was not restored!');
      console.log(`   Before refresh: ${messagesBefore} messages`);
      console.log(`   After refresh: ${messagesAfter} messages`);
    }

    // Step 9: Test the API endpoint directly
    console.log('\nStep 9: Testing /chat/history API endpoint...');
    const sessionId = await page.evaluate(() => {
      return sessionStorage.getItem('session_id');
    });

    if (sessionId) {
      console.log(`   Session ID: ${sessionId}`);
      const response = await fetch(`http://localhost:8000/chat/history/${sessionId}`);
      if (response.ok) {
        const history = await response.json();
        console.log(`   ✅ API returned ${history.length} messages`);
        console.log('   History from database:');
        history.forEach((msg, i) => {
          console.log(`      ${i + 1}. [${msg.role.toUpperCase()}] ${msg.content.substring(0, 40)}...`);
        });
      } else {
        console.log(`   ❌ API error: ${response.status}`);
      }
    }

  } catch (error) {
    console.error('❌ Test failed with error:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ Test completed!');
  }
})();
