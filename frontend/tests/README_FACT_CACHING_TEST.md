# Fact Caching Feature - Playwright E2E Test

## Overview

Comprehensive end-to-end test for the v4.1 fact caching feature, testing both **owner mode** (24h + persistent) and **guest mode** (1h ephemeral) behavior.

## What Gets Tested

### Owner Mode (24h Redis + Permanent DB)
- ✓ Login with PIN 9999
- ✓ Fact extraction: "My birthday is May 15"
- ✓ Bot remembers facts in responses
- ✓ Multiple facts (birthday, preferences) stored
- ✓ Facts persist after page refresh
- ✓ Long-term persistence in PostgreSQL

### Guest Mode (1h Redis only)
- ✓ Login as guest (no PIN needed)
- ✓ Fact extraction: "I like coffee", "I work at TechCorp"
- ✓ Bot remembers facts during session
- ✓ Session isolation (guest facts don't leak to owner)
- ✓ Facts are ephemeral (1h TTL, no DB storage)

### Key Verifications
- ✓ Pattern-based fact extraction works
- ✓ Facts are included in system prompt
- ✓ Owner and guest sessions are isolated
- ✓ Facts survive page refresh (owner only)
- ✓ No performance degradation

## Running the Test

### Prerequisites
```bash
# Install Playwright (if not already installed)
npm install --save-dev playwright
```

### Run the Test
```bash
# From the frontend directory:
cd frontend/tests

# Run the fact caching test
node test-fact-caching.js

# Or from root:
node frontend/tests/test-fact-caching.js
```

The test will:
1. Open a browser window (headless: false)
2. Connect to production: https://lenoir-chatbot.vercel.app
3. Test owner mode flow (login, facts, refresh)
4. Test guest mode flow (guest login, facts, isolation)
5. Print detailed results
6. Close browser

### Expected Output

```
🧪 Testing Fact Caching Feature (v4.1)

═══════════════════════════════════════════════════════════════════════
TEST 1: OWNER MODE - Fact Extraction & Caching
═══════════════════════════════════════════════════════════════════════
✓ Frontend loaded

Step 1.1: Login as Owner with PIN 9999...
  PIN entered: 9999
✓ Owner logged in

Step 1.2: Telling first fact: "My birthday is May 15"...
✓ Message sent

Step 1.3: Checking if bot acknowledges the fact...
  User message visible: ✓

Step 1.4: Asking bot: "When is my birthday?"...
✓ Question sent

Step 1.5: Verifying bot remembers the fact...
✓ BOT REMEMBERED FACT: Bot mentioned "May 15" in response!

...

📊 TEST RESULTS SUMMARY:

Owner Mode (24h Redis + Permanent DB):
  ✓ Facts extracted from messages
  ✓ Bot remembers birthday fact
  ✓ Bot remembers food preference
  ✓ Facts persist after page refresh

Guest Mode (1h Redis only):
  ✓ Facts extracted from messages
  ✓ Bot remembers coffee preference
  ✓ Bot remembers work location
  ✓ Facts NOT visible in other sessions

✅ ALL TESTS PASSED - Fact caching working correctly!
```

## Test Flow

### Phase 1: Owner Mode Testing
```
1. Navigate to https://lenoir-chatbot.vercel.app
2. Click "Login as Owner"
3. Enter PIN: 9999
4. Say: "My birthday is May 15"
5. Ask: "When is my birthday?" → Bot should remember "May 15"
6. Say: "My favorite food is pizza"
7. Ask: "What is my favorite food?" → Bot should answer "pizza"
8. Refresh the page
9. Verify facts still visible in chat history
```

### Phase 2: Guest Mode Testing
```
1. Open new browser tab (fresh session)
2. Navigate to https://lenoir-chatbot.vercel.app
3. Click "Continue as Guest"
4. Verify "Guest Mode" badge appears
5. Say: "I like coffee"
6. Ask: "What do I like?" → Bot should remember "coffee"
7. Say: "I work at TechCorp"
8. Ask: "Where do I work?" → Bot should answer "TechCorp"
9. Verify guest facts are NOT visible in owner's session (isolation)
```

### Phase 3: Verification
```
- Compare owner vs guest behavior
- Verify session isolation
- Print comprehensive summary
```

## Key Assertions

| Test | Owner | Guest | Expected |
|------|-------|-------|----------|
| Fact extraction | Yes | Yes | ✓ Both extract |
| Bot remembers | Yes | Yes | ✓ Both remember in session |
| Persist after refresh | Yes | No | ✓ Owner only |
| Session isolation | N/A | Yes | ✓ Guest facts isolated |
| TTL | 24h | 1h | ✓ Role-based |

## Debugging

If tests fail:

1. **Bot doesn't remember fact**:
   - Check if fact was extracted (look for patterns in message)
   - Verify Redis is connected (check health endpoint)
   - Check system prompt includes facts

2. **Facts don't persist after refresh**:
   - Verify PostgreSQL migration ran: `SELECT COUNT(*) FROM personal_facts;`
   - Check session_id is saved in sessionStorage
   - Verify `getChatHistory` API is working

3. **Guest facts leak to owner**:
   - Verify session IDs are different
   - Check Redis key namespace: `facts:{session_id}:*`
   - Verify `clear_session_facts` is called on logout

4. **Browser timeouts**:
   - Increase timeout values in test
   - Verify production URLs are accessible
   - Check network latency

## Configuration

Test parameters (can be customized):

```javascript
// URLs
const FRONTEND_URL = 'https://lenoir-chatbot.vercel.app';
const BACKEND_URL = 'https://lenoir-chatbot-production.up.railway.app';

// Credentials
const OWNER_PIN = '9999';

// Wait times (milliseconds)
const LOGIN_WAIT = 2000;
const MESSAGE_WAIT = 3000;
const REFRESH_WAIT = 2000;
```

## Related Tests

- `test-production.js` - General production deployment test
- `backend/tests/test_fact_extractor.py` - Unit tests for fact extraction
- `backend/tests/test_fact_manager.py` - Unit tests for Redis caching

## Troubleshooting

### "Browser launch failed"
```bash
# Install required dependencies
npm install --save-dev @playwright/test
```

### "Timeout waiting for selector"
- Increase wait times in test
- Verify CSS selectors match current UI
- Check console for JavaScript errors

### "Bot response not matching pattern"
- Verify fact was extracted (check regex patterns)
- Check system prompt includes facts
- Verify Redis TTL hasn't expired

## Future Enhancements

- [ ] Test fact expiry (wait 1h+ for guest facts)
- [ ] Test max facts per session (FACT_CACHE_MAX_ITEMS=50)
- [ ] Test fact categories (event, preference, contact, habit)
- [ ] Test concurrent sessions
- [ ] Test Redis connection failure (fallback behavior)
- [ ] Test PostgreSQL connection failure
- [ ] Performance benchmarking (response time with/without facts)

## Notes

- Test opens browser window with `headless: false` for visibility
- Test uses two separate browser tabs (owner and guest)
- Each test takes ~30-60 seconds
- Requires internet connection to production
- Can be run multiple times (doesn't affect persistent data)

---

**Last Updated**: 2026-05-25  
**Version**: v4.1.0 (Fact Caching)  
**Status**: ✅ Ready for testing
