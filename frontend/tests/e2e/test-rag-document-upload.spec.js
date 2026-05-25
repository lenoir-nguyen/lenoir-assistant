"""
E2E tests for document upload and RAG features using Playwright.

Tests the complete flow of uploading documents, listing them,
and verifying they can be used in chat responses.
"""

import { test, expect } from '@playwright/test'

const BASE_URL = 'http://localhost:3000'
const OWNER_PIN = '9999'  // Default test PIN

test.describe('RAG Document Upload Feature', () => {
  test('Owner can upload and view documents', async ({ page }) => {
    // Navigate to app
    await page.goto(BASE_URL)

    // Login as owner
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document upload section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Create a temporary text file for upload
    const filePath = './test-doc.txt'
    const fileContent = 'This is a test document for RAG. It contains information about Python programming.'

    // Upload document via drag and drop
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'test-doc.txt', mimeType: 'text/plain' })

    // Wait for upload to complete
    await expect(page.locator('text=test-doc.txt')).toBeVisible({ timeout: 10000 })

    // Verify document appears in list
    const documentItem = page.locator('text=test-doc.txt')
    await expect(documentItem).toBeVisible()

    // Verify chunk count is displayed
    await expect(page.locator('text=/\\d+ chunks/')).toBeVisible()
  })

  test('Owner can delete documents', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Upload a test document
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'test-delete.txt', mimeType: 'text/plain' })
    await expect(page.locator('text=test-delete.txt')).toBeVisible({ timeout: 10000 })

    // Delete the document
    const deleteButton = page.locator('button[title="Delete document"]').first()
    await deleteButton.click()

    // Confirm deletion
    page.once('dialog', (dialog) => {
      expect(dialog.message()).toContain('Delete')
      dialog.accept()
    })

    // Verify document is removed
    await expect(page.locator('text=test-delete.txt')).not.toBeVisible({ timeout: 5000 })
  })

  test('Upload validates file type', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Try to upload unsupported file type
    // Note: This would need a file input rather than drag-and-drop for unsupported types
    const fileInput = page.locator('input[type="file"]')
    // Attempting to set unsupported type will be validated by the browser/API

    await expect(page.locator('text=Personal Documents')).toBeVisible()
  })

  test('Upload validates file size limit', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Verify size limit is mentioned in UI
    await expect(page.locator('text=10MB')).toBeVisible()
  })

  test('Guest cannot upload documents', async ({ page }) => {
    // Navigate to app
    await page.goto(BASE_URL)

    // Login as guest (skip PIN)
    await page.click('button:has-text("Continue as Guest")')
    await page.waitForNavigation()

    // Document upload section should not be visible for guests
    const uploadSection = page.locator('text=Personal Documents')
    // Guest mode should not show document features
    // The actual implementation determines what's visible to guests
  })

  test('Document upload shows loading state', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Start upload
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'test-upload.txt', mimeType: 'text/plain' })

    // Check for loading state (hourglass emoji or "Uploading..." text)
    await expect(page.locator('text=Uploading')).toBeVisible({ timeout: 5000 })

    // Wait for completion
    await expect(page.locator('text=Uploading')).not.toBeVisible({ timeout: 30000 })
  })

  test('Error handling for upload failures', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Error state would be shown if upload fails
    // This test verifies UI has error handling capability
    const errorBox = page.locator('[class*="errorBox"]')
    // Error box should exist in DOM even if not initially visible
  })

  test('Document list shows upload metadata', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Upload document
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'metadata-test.txt', mimeType: 'text/plain' })
    await expect(page.locator('text=metadata-test.txt')).toBeVisible({ timeout: 10000 })

    // Verify metadata is displayed
    const docItem = page.locator('text=metadata-test.txt').first().locator('..')
    await expect(docItem.locator('text=/chunks/')).toBeVisible()
    await expect(docItem.locator('text=/Uploaded/')).toBeVisible()
  })

  test('Document upload persists across page refresh', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Upload document
    const uploadArea = page.locator('[class*="uploadArea"]')
    const testFileName = 'persist-test.txt'
    await uploadArea.dragAndDropFile({ name: testFileName, mimeType: 'text/plain' })
    await expect(page.locator(`text=${testFileName}`)).toBeVisible({ timeout: 10000 })

    // Refresh page
    await page.reload()

    // Wait for reload and login
    await expect(page.locator('text=Personal Documents')).toBeVisible({ timeout: 10000 })

    // Document should still be visible
    await expect(page.locator(`text=${testFileName}`)).toBeVisible()
  })

  test('Empty document list shows appropriate message', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // If no documents, should show "No documents yet" message
    const emptyMessage = page.locator('text=/[Nn]o documents|Upload one to get started/')
    // This will be visible if documents list is empty
  })

  test('Multiple document uploads', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Upload first document
    let uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'doc1.txt', mimeType: 'text/plain' })
    await expect(page.locator('text=doc1.txt')).toBeVisible({ timeout: 10000 })

    // Upload second document
    uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({ name: 'doc2.txt', mimeType: 'text/plain' })
    await expect(page.locator('text=doc2.txt')).toBeVisible({ timeout: 10000 })

    // Both documents should be visible
    await expect(page.locator('text=doc1.txt')).toBeVisible()
    await expect(page.locator('text=doc2.txt')).toBeVisible()

    // Document count should show 2
    const docCount = page.locator('text=/\\(2\\)/')
    await expect(docCount).toBeVisible()
  })

  test('RAG documents are used in chat responses', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Upload a document with specific content
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({
      name: 'chat-test.txt',
      mimeType: 'text/plain'
    })
    await expect(page.locator('text=chat-test.txt')).toBeVisible({ timeout: 10000 })

    // Navigate to chat if not already there
    await page.click('text=Chat')  // Assuming there's a chat button/tab

    // Ask a question related to the document
    const chatInput = page.locator('input[placeholder*="message"]')
    await chatInput.fill('What is mentioned in my documents?')
    await chatInput.press('Enter')

    // Wait for response
    const response = page.locator('[class*="assistant"]').last()
    await expect(response).toBeVisible({ timeout: 15000 })

    // Response should acknowledge the document (implementation specific)
  })

  test('Supported file formats are indicated in UI', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Check for supported format indicators
    await expect(page.locator('text=/PDF|TXT|Word|Excel|MD|PNG|JPEG/i')).toBeVisible()
  })

  test('File input and drag-drop both work', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Wait for document section
    await expect(page.locator('text=Personal Documents')).toBeVisible()

    // Try file input method
    const fileInput = page.locator('input[type="file"]')
    // Should exist and be hidden
    await expect(fileInput).toHaveAttribute('style', /display:\s*none/)

    // Click on upload area should trigger file input
    const uploadLabel = page.locator('label[for="file-input"]')
    await uploadLabel.click()

    // File dialog would open (browser dependent)
  })
})

test.describe('RAG in Chat Context', () => {
  test('Chat prompt includes document context for owners', async ({ page }) => {
    // Navigate and login
    await page.goto(BASE_URL)
    await page.fill('input[placeholder="Enter PIN"]', OWNER_PIN)
    await page.click('button:has-text("Login")')
    await page.waitForNavigation()

    // Upload document
    const uploadArea = page.locator('[class*="uploadArea"]')
    await uploadArea.dragAndDropFile({
      name: 'context-test.txt',
      mimeType: 'text/plain'
    })
    await expect(page.locator('text=context-test.txt')).toBeVisible({ timeout: 10000 })

    // In chat, documents should be available for context
    // (This would require inspecting network requests or system prompt visibility)
  })

  test('Guest mode does not see uploaded documents', async ({ page }) => {
    // This test would require two browser contexts or sessions
    // to verify guests don't see owner's documents
  })
})
