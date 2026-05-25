"""
Document upload and management endpoints for RAG system.

Allows owners to upload documents, list them, and delete them.
Documents are automatically chunked and embedded for semantic search.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
import os
from config import get_settings
from db.session import get_db
from db.models import Document, DocumentChunk
from routers.auth import get_is_owner
from services.file_storage import get_file_storage
from services.document_processor import DocumentProcessor
from services.vectorstore import store_chunk
from sqlalchemy import select

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


# ============================================================================
# Data Models
# ============================================================================

class DocumentMetadata(BaseModel):
    """Response model for document metadata."""
    id: str
    filename: str
    description: str | None = None
    uploaded_at: str
    chunk_count: int = 0


class DocumentUploadResponse(BaseModel):
    """Response from document upload."""
    document_id: str
    filename: str
    chunk_count: int
    message: str


class DocumentChunkResponse(BaseModel):
    """Response model for document chunk."""
    id: str
    content: str
    source_type: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: str = None,
    http_request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for RAG system.

    Owner only. Automatically chunks and embeds for semantic search.

    Supported formats: PDF, TXT, Markdown, Word, Excel, PNG, JPEG

    Args:
        file: File to upload
        description: Optional document description
        http_request: FastAPI request (auth check)
        db: Database session

    Returns:
        DocumentUploadResponse with document_id and chunk_count

    Raises:
        HTTPException: 401 if not owner, 400 if invalid format/size, 500 if processing fails
    """
    try:
        # Step 1: Check owner authorization
        if http_request is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        is_owner = await get_is_owner(http_request)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can upload documents")

        # Step 2: Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        supported = DocumentProcessor.get_supported_formats()

        if file_ext not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported: {', '.join(supported)}"
            )

        # Check file size
        file_bytes = await file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        max_size = settings.MAX_DOCUMENT_SIZE_MB

        if file_size_mb > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_size}MB"
            )

        # Step 3: Store document metadata
        document_id = uuid4()
        document = Document(
            id=document_id,
            filename=file.filename,
            description=description
        )
        db.add(document)
        await db.flush()  # Flush to get the document ID

        # Step 4: Save file to storage
        storage = get_file_storage()
        storage_path = f"documents/{document_id}/{file.filename}"

        try:
            await storage.upload(file_bytes, storage_path)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )

        # Step 5: Process document (extract text and chunk)
        try:
            # Save file temporarily for processing
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)

            # Extract text
            full_text = await DocumentProcessor.process_document(temp_path, file_ext)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # Split into chunks
            chunks = DocumentProcessor.chunk_text(full_text)

            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail="Document is empty or couldn't be parsed"
                )

            # Step 6: Embed and store chunks
            chunk_count = 0
            for chunk_text in chunks:
                try:
                    await store_chunk(
                        db,
                        source_type='document',
                        source_id=document_id,
                        content=chunk_text
                    )
                    chunk_count += 1
                except Exception as e:
                    print(f"[upload_document] Error storing chunk: {str(e)}")
                    # Continue processing other chunks even if one fails

            # Step 7: Commit all changes
            await db.commit()

            return DocumentUploadResponse(
                document_id=str(document_id),
                filename=file.filename,
                chunk_count=chunk_count,
                message=f"Successfully uploaded {file.filename} with {chunk_count} chunks"
            )

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            print(f"[upload_document] Error processing document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[upload_document] FATAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=list[DocumentMetadata])
async def list_documents(
    http_request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all uploaded documents (owner only).

    Args:
        http_request: FastAPI request (auth check)
        db: Database session

    Returns:
        List of document metadata with chunk counts

    Raises:
        HTTPException: 401 if not owner, 500 if database fails
    """
    try:
        # Check owner authorization
        if http_request is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        is_owner = await get_is_owner(http_request)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can view documents")

        # Query all documents
        stmt = select(Document).order_by(Document.uploaded_at.desc())
        result = await db.execute(stmt)
        documents = result.scalars().all()

        # Get chunk counts for each document
        response = []
        for doc in documents:
            chunk_stmt = select(DocumentChunk).where(
                DocumentChunk.source_type == 'document',
                DocumentChunk.source_id == doc.id
            )
            chunk_result = await db.execute(chunk_stmt)
            chunk_count = len(chunk_result.scalars().all())

            response.append(DocumentMetadata(
                id=str(doc.id),
                filename=doc.filename,
                description=doc.description,
                uploaded_at=doc.uploaded_at.isoformat(),
                chunk_count=chunk_count
            ))

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"[list_documents] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    http_request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document and all associated chunks (owner only).

    Args:
        document_id: UUID of document to delete
        http_request: FastAPI request (auth check)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 401 if not owner, 404 if not found, 500 if deletion fails
    """
    try:
        # Check owner authorization
        if http_request is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        is_owner = await get_is_owner(http_request)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can delete documents")

        # Parse document ID
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid document ID format")

        # Get document
        stmt = select(Document).where(Document.id == doc_uuid)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete all associated chunks
        chunk_stmt = select(DocumentChunk).where(
            DocumentChunk.source_type == 'document',
            DocumentChunk.source_id == doc_uuid
        )
        chunk_result = await db.execute(chunk_stmt)
        chunks = chunk_result.scalars().all()

        for chunk in chunks:
            await db.delete(chunk)

        # Delete document metadata
        await db.delete(document)
        await db.commit()

        return {
            "message": f"Document '{document.filename}' deleted",
            "deleted_chunks": len(chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[delete_document] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    document_id: str,
    http_request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all chunks for a specific document (owner only).

    Args:
        document_id: UUID of document
        http_request: FastAPI request (auth check)
        db: Database session

    Returns:
        List of document chunks with content

    Raises:
        HTTPException: 401 if not owner, 404 if not found, 500 if query fails
    """
    try:
        # Check owner authorization
        if http_request is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        is_owner = await get_is_owner(http_request)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can view document chunks")

        # Parse document ID
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid document ID format")

        # Verify document exists
        doc_stmt = select(Document).where(Document.id == doc_uuid)
        doc_result = await db.execute(doc_stmt)
        if not doc_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Document not found")

        # Get chunks
        chunk_stmt = select(DocumentChunk).where(
            DocumentChunk.source_type == 'document',
            DocumentChunk.source_id == doc_uuid
        ).order_by(DocumentChunk.created_at)

        chunk_result = await db.execute(chunk_stmt)
        chunks = chunk_result.scalars().all()

        return [
            DocumentChunkResponse(
                id=str(chunk.id),
                content=chunk.content[:500],  # Truncate for preview
                source_type=chunk.source_type
            )
            for chunk in chunks
        ]

    except HTTPException:
        raise
    except Exception as e:
        print(f"[get_document_chunks] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")
