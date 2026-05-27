# Lenoir Chatbot v5 — Manual Testing Guide
**Date**: 2026-05-26  
**Status**: v5.0.0 Production Deployment  
**Frontend**: https://lenoir-chatbot.vercel.app  
**Backend**: https://lenoir-chatbot-production.up.railway.app

---

## 📋 Test Coverage Summary

### ✅ **Features Confirmed Working (13/16 automated tests passing)**

1. ✅ Frontend loads correctly
2. ✅ Owner authentication (PIN: 9999)
3. ✅ Guest mode access
4. ✅ UI badges (Owner Mode 🔐 / Guest Mode 👤)
5. ✅ Clear conversation button
6. ✅ Logout button
7. ✅ Responsive design (mobile works)
8. ✅ Document panel toggle (owner-only)
9. ✅ Chat input field
10. ✅ Chat message send (basic)
11. ✅ Message display
12. ✅ Document upload UI appears
13. ✅ Logout functionality

### ⚠️ **Known Issues (3/16 tests failing)**

1. ❌ **Document Upload** — Files not appearing in list after upload
2. ❌ **RAG Chat** — Chat returns error when documents needed
3. ❌ **Guest API Protection** — API returns unexpected status code

---

## 🧪 Manual Testing Procedure

### **Part 1: Basic Authentication & UI (5 minutes)**

#### Test 1A: Login as Owner
1. Open https://lenoir-chatbot.vercel.app
2. Click **"🔐 Login as Owner"** button
3. Enter PIN: **9999**
4. Click **"✓ Verify PIN"** button
5. **Expected**: 
   - ✅ Chat window loads
   - ✅ Header shows "🔐 Owner Mode"
   - ✅ Chat welcome message: "Welcome back! I'm Lenoir's secret assistant..."
   - ✅ Buttons visible: "📚 Show Documents", "🗑️ Clear", "🚪 Logout"

#### Test 1B: Guest Mode
1. Refresh page (Ctrl+R)
2. Click **"👤 Continue as Guest"** button
3. **Expected**:
   - ✅ Chat window loads
   - ✅ Header shows "👤 Guest Mode"
   - ✅ Chat welcome message: "Welcome! I'm Lenoir's assistant. (Anonymous mode)..."
   - ✅ NO "📚 Documents" button visible
   - ✅ Only "🗑️ Clear" and "🚪 Logout" buttons visible

#### Test 1C: Logout
1. (Still in Guest mode) Click **"🚪 Logout"** button
2. **Expected**: 
   - ✅ Returns to login screen
   - ✅ Shows "🔐 Login as Owner" and "👤 Continue as Guest" buttons

---

### **Part 2: Chat Functionality (5 minutes)**

#### Test 2A: Basic Chat (Guest Mode)
1. Click **"👤 Continue as Guest"**
2. Type in chat input: **"Hello, how are you?"**
3. Click **"Send"** button
4. **Expected**:
   - ✅ Your message appears as blue bubble on right
   - ✅ AI response appears as gray bubble on left (takes ~3-5 seconds)
   - ✅ Both have timestamps
   - ✅ AI response is not empty

#### Test 2B: Multiple Messages (Owner Mode)
1. Log in as owner (PIN: 9999)
2. Send message 1: **"What is your name?"**
3. Wait for response (~3-5 seconds)
4. Send message 2: **"What's the date today?"**
5. Wait for response
6. **Expected**:
   - ✅ Both messages and responses appear
   - ✅ Conversation flows naturally
   - ✅ AI remembers context (if it mentions earlier conversation)

#### Test 2C: Clear Conversation
1. (Still as owner) Click **"🗑️ Clear"** button
2. **Expected**:
   - ✅ All messages disappear
   - ✅ Only welcome message remains: "Welcome back! I'm Lenoir's secret assistant..."

---

### **Part 3: Document Management (10 minutes)**

#### Test 3A: Document Panel Opens
1. (As owner) Click **"📚 Show Documents"** button
2. **Expected**:
   - ✅ Panel appears below header
   - ✅ Title: "📚 Personal Documents (Owner Only)"
   - ✅ Subtitle: "Upload documents for the AI to reference..."
   - ✅ Upload area visible: "📤 Drag and drop files here or click to browse"
   - ✅ File types listed: "Supported: PDF, TXT, MD, Word, Excel, PNG, JPEG (max 10MB)"
   - ✅ Section below: "Uploaded Documents (0)" with "No documents yet" message

#### Test 3B: Panel Toggle
1. Click **"📚 Hide Documents"** button
2. **Expected**: Document panel disappears
3. Click **"📚 Show Documents"** again
4. **Expected**: Panel reappears

#### Test 3C: Upload Test Document
1. (Panel open) Create a test file locally:
   ```
   Save as: test.txt
   Content:
   Lenoir Chatbot Test Document
   Created: May 2026
   Status: Production v5
   ```
2. Click in upload area or drag file there
3. Select the test.txt file
4. **Expected**:
   - ⏳ Upload starts (⏳ Uploading... shown)
   - ⏳ Wait 5-10 seconds for processing
   - ✅ File appears in "Uploaded Documents" list
   - ✅ Shows filename: "📄 test.txt"
   - ✅ Shows chunk count: "X chunks"
   - ✅ Shows upload date: "Uploaded 5/26/2026"
   - ✅ Delete button (🗑️) appears next to file

**⚠️ If test.txt does NOT appear**:
   - This is **ISSUE #1** (Document Upload)
   - Check browser console for errors (F12)
   - Check backend logs in Railway
   - Skip to Test 3D for now

#### Test 3D: Multiple Files
1. Create another test file: test2.txt with different content
2. Upload it the same way
3. **Expected**: Both files appear in list

**⚠️ If files don't appear**: Confirm ISSUE #1 exists

#### Test 3E: Delete Document
1. If document uploaded, click delete button (🗑️) next to it
2. Confirm deletion in popup dialog
3. **Expected**:
   - ✅ Popup appears: "Delete 'test.txt'? This action cannot be undone."
   - ✅ After confirmation, file disappears from list
   - ✅ Document count decreases: "Uploaded Documents (0)"

#### Test 3F: File Validation
1. Try uploading an invalid file (e.g., .exe, .zip)
2. **Expected**: Error message: "❌ Unsupported file type. Supported: PDF, TXT, MD, Word, Excel, PNG, JPEG"

#### Test 3G: File Size Limit
1. Create a file larger than 10MB
2. Try to upload
3. **Expected**: Error message: "❌ File too large. Max size is 10MB"

---

### **Part 4: RAG (Document Context in Chat) — ISSUE #2**

#### Test 4A: Upload & Chat (if documents work)
1. Upload test document with specific content:
   ```
   My favorite color is blue.
   I work at Acme Corporation.
   My birthday is May 15, 1990.
   ```
2. Hide document panel
3. In chat, ask: **"What's my favorite color?"**
4. **Expected**:
   - ✅ AI responds with information from document: "Your favorite color is blue"
   - ⚠️ If AI says "I don't know", this is ISSUE #2

#### Test 4B: Multiple Documents
1. Upload 2-3 documents with different information
2. Ask: **"Tell me everything you know about me"**
3. **Expected**: AI mentions facts from all documents

**⚠️ If chat returns "Sorry, I encountered an error"**:
   - This is **ISSUE #2** (RAG Context in Chat)
   - Likely caused by ISSUE #1 (documents not uploading)

---

### **Part 5: Access Control — ISSUE #3**

#### Test 5A: Guest Cannot Upload
1. Log in as guest
2. **Expected**: NO document button visible anywhere
3. ✅ Confirms guests can't access upload feature

#### Test 5B: Guest Cannot Access API
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Paste and run:
   ```javascript
   fetch('https://lenoir-chatbot-production.up.railway.app/documents', {
     method: 'GET',
     headers: { 'Content-Type': 'application/json' }
   }).then(r => console.log('Status:', r.status, r.statusText))
   ```
4. **Expected**: Status should be 401 (Unauthorized) or 403 (Forbidden)

**⚠️ If status is 200 or something else**: This is **ISSUE #3**

#### Test 5C: Owner API Access
1. Still in browser console, get your auth token:
   ```javascript
   sessionStorage.getItem('auth_token')
   ```
2. Copy the token value
3. Run:
   ```javascript
   fetch('https://lenoir-chatbot-production.up.railway.app/documents', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer YOUR_TOKEN_HERE`
     }
   }).then(r => r.json()).then(d => console.log('Documents:', d))
   ```
4. **Expected**: Should return array of documents (or empty array if none)

---

## 🔍 Debug Information

### Browser Console Errors
1. Press F12 to open Developer Tools
2. Go to "Console" tab
3. Check for red error messages
4. Note any errors in your report

### Backend Logs (for site admin)
```bash
# SSH into Railway backend
cd /app

# View recent logs
railway logs --follow

# Look for errors containing:
# - "document"
# - "upload"
# - "pgvector"
# - "storage"
```

### Network Requests (for debugging)
1. Open Developer Tools (F12)
2. Go to "Network" tab
3. When you upload a document, check:
   - Request: `POST /documents/upload`
   - Response status: Should be 200-201
   - Response body: Should show document_id, filename, chunk_count

---

## 📊 Issue Report Template

Copy this for each issue found:

```
## Issue #[NUMBER]
**Title**: [Brief description]
**Severity**: Critical / High / Medium / Low
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior**: [What should happen]
**Actual Behavior**: [What actually happened]
**Evidence**: [Screenshot or console error]
**Environment**: 
- Browser: [Chrome/Firefox/Safari]
- Device: [Desktop/Mobile]
- Date Tested: [YYYY-MM-DD]
```

---

## ✅ Manual Test Checklist

Mark as you complete:

### Authentication (5 points)
- [ ] Login as Owner works
- [ ] Guest mode works  
- [ ] Mode badges correct
- [ ] Logout works
- [ ] Can re-login after logout

### Chat (5 points)
- [ ] Chat input accepts text
- [ ] Send button works
- [ ] Messages display correctly
- [ ] AI responds (not empty)
- [ ] Clear button works

### Documents UI (5 points)
- [ ] Show/Hide toggle works
- [ ] Upload area displays
- [ ] File input works
- [ ] Drag-and-drop appears
- [ ] Error messages display

### Documents Upload (3 points) — ⚠️ KNOWN ISSUE #1
- [ ] Can select file
- [ ] Upload starts (⏳ shows)
- [ ] File appears in list after upload

### RAG Features (2 points) — ⚠️ KNOWN ISSUE #2
- [ ] Chat uses document content
- [ ] AI cites document information

### Access Control (3 points) — ⚠️ KNOWN ISSUE #3
- [ ] Guest has no document button
- [ ] Owner can access documents
- [ ] API returns proper auth errors

### Responsive (2 points)
- [ ] Desktop view works
- [ ] Mobile view works
- [ ] All buttons accessible on mobile

---

## 🎯 Summary of Known Issues

### ISSUE #1: Document Upload
- **Status**: ❌ BLOCKING
- **Impact**: Cannot test RAG features
- **Symptoms**: Files upload but don't appear in list
- **Likely Cause**: Backend document processing or file storage failing
- **Fix Required**: 
  - Check Railway backend logs
  - Verify pgvector extension enabled
  - Check file storage configuration
  - Verify database migration ran: `alembic current`

### ISSUE #2: RAG in Chat
- **Status**: ❌ BLOCKED by ISSUE #1
- **Impact**: Can't test document context in responses
- **Symptoms**: Chat returns "Sorry, I encountered an error"
- **Likely Cause**: Document processing failed (ISSUE #1)
- **Fix Required**: Fix ISSUE #1 first

### ISSUE #3: Guest API Protection
- **Status**: ⚠️ POTENTIAL SECURITY ISSUE
- **Impact**: Guest access control not working properly
- **Symptoms**: API returns unexpected status codes
- **Likely Cause**: Missing auth header validation or CORS issue
- **Fix Required**:
  - Review `/documents` endpoint auth check
  - Verify CORS configuration
  - Check Authorization header handling

---

## 🚀 Next Actions

### For User (Testing):
1. Follow this guide manually
2. Document any issues found
3. Note screenshots/errors
4. Report results

### For Developer (Fixing):
1. Fix ISSUE #1 (document upload) FIRST
   - Check backend logs
   - Verify pgvector migration
   - Test document endpoint manually
   
2. Fix ISSUE #2 (RAG chat)
   - Should auto-fix once ISSUE #1 is fixed
   
3. Fix ISSUE #3 (API auth)
   - Review auth middleware
   - Add proper 401/403 responses

---

## 📞 Support

**Testing Questions**: Refer to section that matches your issue  
**Backend Issues**: Check Railway logs  
**Frontend Issues**: Check browser DevTools Console (F12)  

**Status Page**: https://lenoir-chatbot.vercel.app (health check)

---

*Last Updated: 2026-05-26*  
*v5.0.0 — RAG System Deployment*
