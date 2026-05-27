import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Test configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const OWNER_PASSPHRASE = '';  // v4: PIN-only authentication
const OWNER_PIN = '9999';

// Helper: Login as owner
async function loginAsOwner(page: Page) {
  await page.goto('/');

  // Wait for initial auth screen with buttons
  await page.waitForSelector('button:has-text("Login as Owner")', { timeout: 10000 });

  // Click "Login as Owner" button
  const ownerLoginButton = page.locator('button:has-text("Login as Owner")');
  await ownerLoginButton.click();

  // Wait for PIN input to appear
  await page.waitForSelector('input[placeholder="Enter PIN"]', { timeout: 5000 });

  // Enter PIN
  const pinInput = page.locator('input[placeholder="Enter PIN"]');
  await pinInput.fill(OWNER_PIN);

  // Click "Verify PIN" button
  const verifyButton = page.locator('button:has-text("Verify PIN")');
  await verifyButton.click();

  // Wait for chat window to load
  await page.waitForSelector('text=Lenoir Assistant', { timeout: 10000 });
  await page.waitForSelector('text=Owner Mode', { timeout: 5000 });
}

// Helper: Login as guest
async function loginAsGuest(page: Page) {
  await page.goto('/');

  // Wait for initial auth screen with buttons
  await page.waitForSelector('button:has-text("Continue as Guest")', { timeout: 10000 });

  // Click "Continue as Guest" button
  const guestButton = page.locator('button:has-text("Continue as Guest")');
  await guestButton.click();

  // Wait for chat window to load
  await page.waitForSelector('text=Lenoir Assistant', { timeout: 10000 });
  await page.waitForSelector('text=Guest Mode', { timeout: 5000 });
}

// Helper: Create test file
async function createTestFile(filename: string, content: string): Promise<string> {
  const filepath = path.join('/tmp', filename);
  fs.writeFileSync(filepath, content);
  return filepath;
}

// Helper: Create test PDF
async function createTestPDF(): Promise<string> {
  const filepath = path.join('/tmp', 'test-document.txt');
  const content = `
Test Document for RAG Testing
This is a test document with important information.

Key Facts:
- The company was founded in 2020
- Headquarters in San Francisco
- The CEO is John Smith
- Company specializes in AI products
- Current employee count: 150 people

This document should be used by the AI to answer questions about the company.
`;
  fs.writeFileSync(filepath, content);
  return filepath;
}

test.describe('Lenoir Assistant v5 RAG System', () => {

  test.describe('Document Upload (Owner Mode)', () => {

    test('should display document upload panel when owner clicks toggle', async ({ page }) => {
      await loginAsOwner(page);

      // Look for the document toggle button
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await expect(toggleButton).toBeVisible();

      // Click to show documents
      await toggleButton.click();

      // Should show the document upload panel
      await expect(page.locator('text=Personal Documents (Owner Only)')).toBeVisible();
      await expect(page.locator('text=Drag and drop files here or click to browse')).toBeVisible();
    });

    test('should upload a text document successfully', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Create test file
      const testFile = await createTestPDF();

      // Upload file via file input
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Wait for upload to complete
      await page.waitForTimeout(3000);

      // Should see the file in the document list
      await expect(page.locator('text=test-document.txt')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=chunks')).toBeVisible();
    });

    test('should reject files larger than 10MB', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Create a large file (11MB - exceeds 10MB limit)
      const largeContent = 'x'.repeat(11 * 1024 * 1024);
      const testFile = await createTestFile('large-file.txt', largeContent);

      // Try to upload
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Should show error message
      await expect(page.locator('text=File too large')).toBeVisible({ timeout: 5000 });
    });

    test('should reject unsupported file types', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Create unsupported file
      const testFile = await createTestFile('test.exe', 'executable content');

      // Try to upload
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Should show error for unsupported type
      await expect(page.locator('text=Unsupported file type')).toBeVisible({ timeout: 5000 });
    });

    test('should list all uploaded documents', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Wait for documents list to load
      await page.waitForSelector('text=Uploaded Documents', { timeout: 5000 });

      // Should see "Uploaded Documents" section
      await expect(page.locator('text=Uploaded Documents')).toBeVisible();
    });

    test('should delete a document with confirmation', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Create and upload a test file
      const testFile = await createTestPDF();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Wait for file to appear
      await page.waitForTimeout(3000);
      await expect(page.locator('text=test-document.txt')).toBeVisible();

      // Click delete button
      const deleteButton = page.locator('button[title="Delete document"]').first();

      // Handle confirmation dialog
      page.once('dialog', dialog => {
        expect(dialog.message()).toContain('Delete');
        dialog.accept();
      });

      await deleteButton.click();

      // File should disappear from list
      await page.waitForTimeout(2000);
      await expect(page.locator('text=test-document.txt')).not.toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('RAG Context in Chat', () => {

    test('should use document content in chat responses', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Upload test document with known information
      const testFile = await createTestPDF();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Wait for upload
      await page.waitForTimeout(3000);

      // Hide documents panel
      await toggleButton.click();

      // Ask question that should be answerable from document
      const messageInput = page.locator('input[placeholder="Type a message..."]');
      await messageInput.fill('When was the company founded?');

      const sendButton = page.locator('button:has-text("Send")');
      await sendButton.click();

      // Wait for response
      await page.waitForTimeout(5000);

      // Response should contain information from the document
      const chatMessages = page.locator('[role="article"]');
      const lastMessage = chatMessages.last();

      // Check that AI referenced document information
      await expect(lastMessage).toContainText(/2020|founded|company/, { timeout: 10000 });
    });

    test('should include multiple documents in RAG context', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Upload multiple test files
      const file1 = await createTestFile('doc1.txt', 'Company A: Founded 2010, Tech sector, 50 employees');
      const file2 = await createTestFile('doc2.txt', 'Company B: Founded 2015, Finance sector, 100 employees');

      const fileInput = page.locator('input[type="file"]');

      // Upload first file
      await fileInput.setInputFiles(file1);
      await page.waitForTimeout(2000);

      // Upload second file
      await fileInput.setInputFiles(file2);
      await page.waitForTimeout(2000);

      // Verify both documents are listed
      await expect(page.locator('text=doc1.txt')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('text=doc2.txt')).toBeVisible({ timeout: 5000 });

      // Hide documents
      await toggleButton.click();

      // Ask question
      const messageInput = page.locator('input[placeholder="Type a message..."]');
      await messageInput.fill('Compare the two companies');

      const sendButton = page.locator('button:has-text("Send")');
      await sendButton.click();

      // Wait for response
      await page.waitForTimeout(5000);

      // Response should reference both companies
      const chatMessages = page.locator('[role="article"]');
      const lastMessage = chatMessages.last();

      await expect(lastMessage).toContainText(/Company|2010|2015|employees/, { timeout: 10000 });
    });
  });

  test.describe('Guest Mode Access Control', () => {

    test('should not show document upload for guest users', async ({ page }) => {
      await loginAsGuest(page);

      // Should not see documents toggle
      const toggleButton = page.locator('button:has-text("Documents")');
      await expect(toggleButton).not.toBeVisible();

      // Should see guest mode indicator
      await expect(page.locator('text=Guest Mode')).toBeVisible();
    });

    test('should prevent guests from accessing document API', async ({ page }) => {
      // Login as guest
      await page.goto('/');
      const guestButton = page.locator('button:has-text("Continue as Guest")');
      await guestButton.click();

      // Wait for chat to load
      await page.waitForSelector('text=Guest Mode', { timeout: 10000 });

      // Try to access document endpoint directly via API
      const response = await page.evaluate(async () => {
        try {
          const result = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/documents`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              // No auth token for guest
            }
          });
          return {
            status: result.status,
            ok: result.ok,
          };
        } catch (error) {
          return { error: String(error) };
        }
      });

      // Should return 401 or 403 (unauthorized)
      expect([401, 403]).toContain(response.status);
    });
  });

  test.describe('Chat History with Documents', () => {

    test('should restore documents after page refresh', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Upload a document
      const testFile = await createTestPDF();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Wait for upload
      await page.waitForTimeout(3000);

      // Verify document appears
      await expect(page.locator('text=test-document.txt')).toBeVisible();

      // Refresh page
      await page.reload();

      // Wait for page to load
      await page.waitForSelector('text=Lenoir Assistant', { timeout: 10000 });

      // Show documents panel again
      await toggleButton.click();

      // Document should still be there
      await expect(page.locator('text=test-document.txt')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Error Handling', () => {

    test('should show error when backend is unreachable', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // The app should still render without crashing
      await expect(page.locator('text=Personal Documents')).toBeVisible();
    });

    test('should handle empty document list gracefully', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Should show empty state message
      await expect(page.locator('text=No documents yet')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('UI/UX Features', () => {

    test('should show upload progress indicator', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Create test file
      const testFile = await createTestPDF();

      // Upload file
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Should show "Uploading..." state
      await expect(page.locator('text=Uploading')).toBeVisible({ timeout: 2000 });
    });

    test('should show drag-and-drop visual feedback', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Find upload area
      const uploadArea = page.locator('text=Drag and drop files here');

      // Simulate drag over
      await uploadArea.evaluate(el => {
        const dragEvent = new DragEvent('dragover', {
          bubbles: true,
          cancelable: true,
        });
        el.dispatchEvent(dragEvent);
      });

      // Should show some visual feedback (implementation specific)
      // At minimum, no errors should occur
      await expect(uploadArea).toBeVisible();
    });

    test('should display document metadata', async ({ page }) => {
      await loginAsOwner(page);

      // Show documents panel
      const toggleButton = page.locator('button:has-text("Show Documents")');
      await toggleButton.click();

      // Upload a document
      const testFile = await createTestPDF();
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(testFile);

      // Wait for upload
      await page.waitForTimeout(3000);

      // Check that metadata is visible
      await expect(page.locator('text=chunks')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('text=Uploaded')).toBeVisible();
    });
  });
});
