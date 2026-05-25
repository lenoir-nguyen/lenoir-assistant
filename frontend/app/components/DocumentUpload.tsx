'use client'

import React, { useState, useEffect } from 'react'
import { uploadDocument, listDocuments, deleteDocument } from '@/lib/api'

interface Document {
  id: string
  filename: string
  description: string | null
  uploaded_at: string
  chunk_count: number
}

export default function DocumentUpload() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  // Load documents on mount
  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      setError(null)
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err: any) {
      setError(err.message || 'Failed to load documents')
      console.error('Error loading documents:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      await handleFileUpload(files[0])
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      await handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    // Validate file type
    const supportedTypes = [
      'application/pdf',
      'text/plain',
      'text/markdown',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'image/png',
      'image/jpeg',
    ]

    if (!supportedTypes.includes(file.type)) {
      setError('Unsupported file type. Supported: PDF, TXT, MD, Word, Excel, PNG, JPEG')
      return
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      setError('File too large. Max size is 10MB')
      return
    }

    try {
      setUploading(true)
      setError(null)
      const result = await uploadDocument(file)
      console.log('Upload successful:', result)
      await loadDocuments()
    } catch (err: any) {
      setError(err.message || 'Failed to upload document')
      console.error('Error uploading document:', err)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Delete "${filename}"? This action cannot be undone.`)) {
      return
    }

    try {
      setError(null)
      await deleteDocument(docId)
      await loadDocuments()
    } catch (err: any) {
      setError(err.message || 'Failed to delete document')
      console.error('Error deleting document:', err)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.panel}>
        {/* Title */}
        <h2 style={styles.title}>📚 Personal Documents (Owner Only)</h2>
        <p style={styles.subtitle}>
          Upload documents for the AI to reference when answering your questions
        </p>

        {/* Upload Area */}
        <div
          style={{
            ...styles.uploadArea,
            ...(dragActive ? styles.uploadAreaActive : {}),
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-input"
            style={styles.fileInput}
            onChange={handleFileChange}
            accept=".pdf,.txt,.md,.docx,.xlsx,.png,.jpg,.jpeg"
            disabled={uploading}
          />
          <label htmlFor="file-input" style={styles.uploadLabel}>
            {uploading ? (
              <>
                <span style={styles.uploadEmoji}>⏳</span>
                <p>Uploading...</p>
              </>
            ) : (
              <>
                <span style={styles.uploadEmoji}>📤</span>
                <p style={styles.uploadText}>
                  Drag and drop files here or click to browse
                </p>
                <p style={styles.uploadSubtext}>
                  Supported: PDF, TXT, MD, Word, Excel, PNG, JPEG (max 10MB)
                </p>
              </>
            )}
          </label>
        </div>

        {/* Error Message */}
        {error && (
          <div style={styles.errorBox}>
            <span>❌ {error}</span>
            <button
              style={styles.closeButton}
              onClick={() => setError(null)}
            >
              ✕
            </button>
          </div>
        )}

        {/* Documents List */}
        <div style={styles.documentsSection}>
          <h3 style={styles.sectionTitle}>
            Uploaded Documents ({documents.length})
          </h3>

          {loading && !error ? (
            <p style={styles.loadingText}>Loading documents...</p>
          ) : documents.length === 0 ? (
            <p style={styles.emptyText}>
              No documents yet. Upload one to get started!
            </p>
          ) : (
            <div style={styles.documentsList}>
              {documents.map((doc) => (
                <div key={doc.id} style={styles.documentItem}>
                  <div style={styles.docInfo}>
                    <p style={styles.docFilename}>📄 {doc.filename}</p>
                    {doc.description && (
                      <p style={styles.docDescription}>{doc.description}</p>
                    )}
                    <p style={styles.docMeta}>
                      {doc.chunk_count} chunks • Uploaded{' '}
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    style={styles.deleteButton}
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto',
  },
  panel: {
    backgroundColor: '#f8f9fa',
    border: '1px solid #e9ecef',
    borderRadius: '8px',
    padding: '20px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '8px',
    color: '#212529',
  },
  subtitle: {
    fontSize: '14px',
    color: '#6c757d',
    marginBottom: '20px',
  },
  uploadArea: {
    border: '2px dashed #dee2e6',
    borderRadius: '8px',
    padding: '40px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backgroundColor: '#fff',
    marginBottom: '20px',
  },
  uploadAreaActive: {
    borderColor: '#007bff',
    backgroundColor: '#e7f1ff',
  },
  fileInput: {
    display: 'none',
  },
  uploadLabel: {
    cursor: 'pointer',
  },
  uploadEmoji: {
    fontSize: '32px',
    display: 'block',
    marginBottom: '10px',
  },
  uploadText: {
    fontSize: '16px',
    fontWeight: '500',
    margin: '10px 0',
    color: '#212529',
  },
  uploadSubtext: {
    fontSize: '12px',
    color: '#6c757d',
  },
  errorBox: {
    backgroundColor: '#f8d7da',
    border: '1px solid #f5c6cb',
    borderRadius: '4px',
    padding: '12px 16px',
    marginBottom: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    color: '#721c24',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: '#721c24',
    cursor: 'pointer',
    fontSize: '18px',
    padding: '0',
  },
  documentsSection: {
    marginTop: '30px',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: '600',
    marginBottom: '15px',
    color: '#212529',
  },
  loadingText: {
    color: '#6c757d',
    fontSize: '14px',
    textAlign: 'center' as const,
  },
  emptyText: {
    color: '#6c757d',
    fontSize: '14px',
    textAlign: 'center' as const,
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '4px',
  },
  documentsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '10px',
  },
  documentItem: {
    backgroundColor: '#fff',
    border: '1px solid #dee2e6',
    borderRadius: '6px',
    padding: '15px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'box-shadow 0.2s ease',
  },
  docInfo: {
    flex: 1,
  },
  docFilename: {
    fontSize: '14px',
    fontWeight: '600',
    margin: '0 0 5px 0',
    color: '#212529',
  },
  docDescription: {
    fontSize: '13px',
    color: '#6c757d',
    margin: '3px 0',
  },
  docMeta: {
    fontSize: '12px',
    color: '#adb5bd',
    margin: '5px 0 0 0',
  },
  deleteButton: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    padding: '8px',
    transition: 'opacity 0.2s ease',
  },
}
