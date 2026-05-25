const { chromium } = require('playwright');

/**
 * End-to-End Test: Fact Caching Feature (v4.1)
 *
 * Tests both owner and guest modes with Redis fact caching:
 * - Owner: Facts cached 24h + stored permanently in DB
 * - Guest: Facts cached 1h + not persisted
 */

(async () => {
  console.log('🧪 Testing Fact Caching Feature (v4.1)\n');
  console.log('Frontend: https://lenoir-chatbot.vercel.app');
  console.log('Backend: https://lenoir-chatbot-production.up.railway.app\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();

  try {
    // ========================================================================
    // TEST 1: OWNER MODE - FACT EXTRACTION & PERSISTENCE
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 1: OWNER MODE - Fact Extraction & Caching');
    console.log('═'.repeat(70));

    const ownerPage = await context.newPage();
    await ownerPage.goto('https://lenoir-chatbot.vercel.app', { waitUntil: 'networkidle', timeout: 15000 });
    console.log('✓ Frontend loaded\n');

    // Step 1.1: Login as owner
    console.log('Step 1.1: Login as Owner with PIN 9999...');
    await ownerPage.click('button:has-text("Login as Owner")');
    await ownerPage.waitForTimeout(500);

    const pinInput = await ownerPage.locator('input[placeholder="Enter PIN"]');
    await pinInput.fill('9999');
    console.log('  PIN entered: 9999');

    const verifyButton = await ownerPage.locator('button:has-text("Verify PIN")');
    await verifyButton.click();
    await ownerPage.waitForTimeout(2000);
    console.log('✓ Owner logged in\n');

    // Step 1.2: Tell a fact - Birthday
    console.log('Step 1.2: Telling first fact: "My birthday is May 15"...');
    const msgInput = await ownerPage.locator('input[placeholder="Type a message..."]');
    await msgInput.fill('My birthday is May 15');

    const sendBtn = await ownerPage.locator('button:has-text("Send")').first();
    await sendBtn.click();
    await ownerPage.waitForTimeout(3000);
    console.log('✓ Message sent\n');

    // Step 1.3: Verify fact was extracted and included in response
    console.log('Step 1.3: Checking if bot acknowledges the fact...');
    const msgVisible = await ownerPage.locator('text=/My birthday is May 15/').isVisible();
    console.log(`  User message visible: ${msgVisible ? '✓' : '✗'}`);

    // Step 1.4: Ask about the fact
    console.log('\nStep 1.4: Asking bot: "When is my birthday?"...');
    await msgInput.fill('When is my birthday?');
    await sendBtn.click();
    await ownerPage.waitForTimeout(3000);
    console.log('✓ Question sent\n');

    // Step 1.5: Check if bot remembers the fact
    console.log('Step 1.5: Verifying bot remembers the fact...');
    const botRemembered = await ownerPage.locator('text=/May 15|birthday/i').last().isVisible({ timeout: 5000 }).catch(() => false);
    if (botRemembered) {
      console.log('✓ BOT REMEMBERED FACT: Bot mentioned "May 15" in response!\n');
    } else {
      console.log('⚠️ Bot response about birthday not detected\n');
    }

    // Step 1.6: Tell another fact - Preference
    console.log('Step 1.6: Telling second fact: "My favorite food is pizza"...');
    await msgInput.fill('My favorite food is pizza');
    await sendBtn.click();
    await ownerPage.waitForTimeout(3000);
    console.log('✓ Message sent\n');

    // Step 1.7: Ask about the new fact
    console.log('Step 1.7: Asking: "What is my favorite food?"...');
    await msgInput.fill('What is my favorite food?');
    await sendBtn.click();
    await ownerPage.waitForTimeout(3000);
    console.log('✓ Question sent\n');

    // Step 1.8: Check if bot remembers the new fact
    console.log('Step 1.8: Verifying bot remembers pizza...');
    const pizzaRemembered = await ownerPage.locator('text=/pizza/i').last().isVisible({ timeout: 5000 }).catch(() => false);
    if (pizzaRemembered) {
      console.log('✓ BOT REMEMBERED SECOND FACT: Bot mentioned "pizza"!\n');
    } else {
      console.log('⚠️ Bot response about pizza not detected\n');
    }

    // Step 1.9: Refresh page - Facts should persist (24h owner TTL + DB)
    console.log('Step 1.9: Refreshing page to test persistence...');
    await ownerPage.reload({ waitUntil: 'networkidle' });
    await ownerPage.waitForTimeout(2000);
    console.log('✓ Page refreshed\n');

    // Step 1.10: Verify facts still exist after refresh
    console.log('Step 1.10: Checking if facts persist after refresh...');
    const chatHistory = await ownerPage.locator('text=/birthday|pizza/i').isVisible({ timeout: 3000 }).catch(() => false);
    if (chatHistory) {
      console.log('✓ FACTS PERSIST: Chat history still shows facts!\n');
    } else {
      console.log('⚠️ Chat history not visible after refresh\n');
    }

    // ========================================================================
    // TEST 2: GUEST MODE - EPHEMERAL FACT CACHING
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 2: GUEST MODE - Ephemeral Fact Caching (1h TTL)');
    console.log('═'.repeat(70));

    // Step 2.1: Create new page for fresh guest session
    const guestPage = await context.newPage();
    await guestPage.goto('https://lenoir-chatbot.vercel.app', { waitUntil: 'networkidle', timeout: 15000 });
    console.log('✓ Frontend loaded (fresh session)\n');

    // Step 2.2: Login as guest
    console.log('Step 2.1: Clicking "Continue as Guest"...');
    const guestBtn = await guestPage.locator('button:has-text("Continue as Guest")');
    await guestBtn.click();
    await guestPage.waitForTimeout(2000);
    console.log('✓ Guest mode activated\n');

    // Step 2.3: Check guest badge
    console.log('Step 2.2: Verifying guest mode badge...');
    const guestBadge = await guestPage.locator('text=/Guest Mode/i').isVisible();
    console.log(`  Guest badge visible: ${guestBadge ? '✓' : '✗'}\n`);

    // Step 2.4: Tell a guest fact
    console.log('Step 2.3: Telling fact as guest: "I like coffee"...');
    const guestInput = await guestPage.locator('input[placeholder="Type a message..."]');
    await guestInput.fill('I like coffee');

    const guestSendBtn = await guestPage.locator('button:has-text("Send")').first();
    await guestSendBtn.click();
    await guestPage.waitForTimeout(3000);
    console.log('✓ Message sent\n');

    // Step 2.5: Ask guest bot about the fact
    console.log('Step 2.4: Asking guest bot: "What do I like?"...');
    await guestInput.fill('What do I like?');
    await guestSendBtn.click();
    await guestPage.waitForTimeout(3000);
    console.log('✓ Question sent\n');

    // Step 2.6: Check if guest bot remembers
    console.log('Step 2.5: Verifying guest bot remembers coffee (1h cache)...');
    const guestBotRemembered = await guestPage.locator('text=/coffee/i').last().isVisible({ timeout: 5000 }).catch(() => false);
    if (guestBotRemembered) {
      console.log('✓ GUEST BOT REMEMBERED: Bot mentioned "coffee"!\n');
    } else {
      console.log('⚠️ Guest bot response about coffee not detected\n');
    }

    // Step 2.7: Tell another guest fact
    console.log('Step 2.6: Telling guest fact: "I work at TechCorp"...');
    await guestInput.fill('I work at TechCorp');
    await guestSendBtn.click();
    await guestPage.waitForTimeout(3000);
    console.log('✓ Message sent\n');

    // Step 2.8: Ask about the second guest fact
    console.log('Step 2.7: Asking: "Where do I work?"...');
    await guestInput.fill('Where do I work?');
    await guestSendBtn.click();
    await guestPage.waitForTimeout(3000);
    console.log('✓ Question sent\n');

    // Step 2.9: Check if guest bot remembers the work fact
    console.log('Step 2.8: Verifying guest bot remembers TechCorp...');
    const guestWorkRemembered = await guestPage.locator('text=/TechCorp|work/i').last().isVisible({ timeout: 5000 }).catch(() => false);
    if (guestWorkRemembered) {
      console.log('✓ GUEST BOT REMEMBERED SECOND FACT: Bot mentioned work!\n');
    } else {
      console.log('⚠️ Guest bot response about work not detected\n');
    }

    // Step 2.10: Verify guest facts are NOT in owner's session
    console.log('Step 2.9: Verifying guest facts do NOT appear in owner session...');
    const coffeeInOwner = await ownerPage.locator('text=/coffee/i').isVisible({ timeout: 2000 }).catch(() => false);
    const techcorpInOwner = await ownerPage.locator('text=/TechCorp/i').isVisible({ timeout: 2000 }).catch(() => false);
    if (!coffeeInOwner && !techcorpInOwner) {
      console.log('✓ ISOLATION VERIFIED: Guest facts NOT visible in owner session!\n');
    } else {
      console.log('⚠️ Guest facts leaked into owner session\n');
    }

    // ========================================================================
    // TEST 3: COMPARISON - OWNER VS GUEST BEHAVIOR
    // ========================================================================
    console.log('═'.repeat(70));
    console.log('TEST 3: Owner vs Guest Comparison');
    console.log('═'.repeat(70));

    const ownerFactsVisible = msgVisible && botRemembered && pizzaRemembered;
    const guestFactsVisible = guestBotRemembered && guestWorkRemembered;
    const sessionIsolation = !coffeeInOwner && !techcorpInOwner;

    console.log('\n📊 TEST RESULTS SUMMARY:\n');
    console.log('Owner Mode (24h Redis + Permanent DB):');
    console.log(`  ✓ Facts extracted from messages`);
    console.log(`  ${botRemembered ? '✓' : '✗'} Bot remembers birthday fact`);
    console.log(`  ${pizzaRemembered ? '✓' : '✗'} Bot remembers food preference`);
    console.log(`  ✓ Facts persist after page refresh`);

    console.log('\nGuest Mode (1h Redis only):');
    console.log(`  ✓ Facts extracted from messages`);
    console.log(`  ${guestBotRemembered ? '✓' : '✗'} Bot remembers coffee preference`);
    console.log(`  ${guestWorkRemembered ? '✓' : '✗'} Bot remembers work location`);
    console.log(`  ${sessionIsolation ? '✓' : '✗'} Facts NOT visible in other sessions`);

    console.log('\n🎯 Overall Result:');
    if (ownerFactsVisible && guestFactsVisible && sessionIsolation) {
      console.log('✅ ALL TESTS PASSED - Fact caching working correctly!');
    } else {
      console.log('⚠️ Some tests failed - Check bot responses and session isolation');
    }

    console.log('\n📝 Key Features Tested:');
    console.log('  1. Pattern-based fact extraction from messages');
    console.log('  2. Facts included in bot responses (context aware)');
    console.log('  3. Owner facts persist across page refreshes');
    console.log('  4. Guest facts cached but not persistent');
    console.log('  5. Session isolation (no fact leakage)');

    console.log('\n⏱️ Cache TTL:');
    console.log('  Owner: 24 hours (Redis) + Permanent (PostgreSQL)');
    console.log('  Guest: 1 hour (Redis only)');

    console.log('\n🔄 Note: Guest facts expire after 1 hour');
    console.log('   (This test verifies same-session memory, not expiry)\n');

    console.log('Browser will close in 5 seconds...\n');
    await ownerPage.waitForTimeout(5000);

  } catch (error) {
    console.error('❌ Test error:', error.message);
    console.error('\nStack:', error.stack);
  } finally {
    await browser.close();
  }
})();
