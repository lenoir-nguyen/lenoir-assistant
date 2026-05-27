# Frontend Tests

E2E tests for the Lenoir Chatbot v5 frontend using Playwright.

## Test Structure

```
frontend/tests/
├── v5-rag/
│   ├── simplified.spec.ts    # Core features tests (13 tests)
│   ├── production.spec.ts    # Full production tests (16 tests)
│   └── full.spec.ts          # Complete E2E suite (deprecated)
└── README.md
```

## Running Tests

### Simplified Tests (Recommended)
Fast, focused tests on working features:

```bash
cd frontend
npm run test -- tests/v5-rag/simplified.spec.ts --reporter=list
```

**Expected Result**: 13 ✅ + 1 ⏱️ (timing) + 3 ⏭️ (skipped)

### Production Tests
Full test suite including known issues:

```bash
cd frontend
npm run test -- tests/v5-rag/production.spec.ts --reporter=list
```

**Expected Result**: 13 ✅ + 3 ❌ (known issues)

### Run All Tests
```bash
cd frontend
npm run test
```

## Test Coverage

### ✅ Working (13 tests)
1. Login page loads
2. Owner authentication (PIN: 9999)
3. Guest authentication
4. Mode badges (Owner & Guest)
5. Clear button functionality
6. Logout button functionality
7. Document toggle (Owner only)
8. Document hidden (Guest)
9. Chat input available
10. Responsive design
11. Chat send & response
12. Show documents panel
13. (additional tests)

### ❌ Known Issues (3 tests)
1. Document Upload - Backend issue #1
2. RAG Context in Chat - Blocked by issue #1
3. Guest API Protection - CORS/auth verification

## Environment Variables

```bash
# .env.local (for local development - git-ignored)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000

# .env.production (for production - committed)
NEXT_PUBLIC_API_URL=https://lenoir-chatbot-production.up.railway.app
NEXT_PUBLIC_FRONTEND_URL=https://lenoir-chatbot.vercel.app
```

## Debug Mode

```bash
# Run with debug output
npm run test -- tests/v5-rag/simplified.spec.ts --debug

# Run with headed browser (see UI)
npm run test:headed

# Run single test
npm run test -- tests/v5-rag/simplified.spec.ts -g "Login"
```

## Test Configuration

See `playwright.config.ts` for:
- Browser configuration (Chromium, Firefox, WebKit)
- Timeout settings
- Retry policy
- Screenshot/video capture

## Troubleshooting

### Tests won't run
```bash
npm install
npm run test
```

### Tests are slow
- Add `--grep "test name"` to run specific test
- Expected duration: 2-3 minutes for full suite

### Can't access the app
- Check frontend is running: `https://lenoir-chatbot.vercel.app`
- Check backend is running: `https://lenoir-chatbot-production.up.railway.app/health`

## Documentation

For comprehensive testing guides, see `docs/testing/`:
- **QUICK_START.md** - 30-second overview
- **SUMMARY.md** - 5-minute summary
- **MANUAL_GUIDE.md** - Step-by-step manual tests
- **PRODUCTION_STATUS.md** - Detailed issue analysis

---

*Last Updated: 2026-05-26*
*v5.0.0 Frontend E2E Tests*
