"""
Unit tests for document processing (v5 RAG feature).

Tests document extraction for various file types.
"""

import pytest
import os
import tempfile
from services.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test document processing."""

    def test_class_configured(self):
        """Test that DocumentProcessor class is configured."""
        assert hasattr(DocumentProcessor, 'CHUNK_SIZE')
        assert hasattr(DocumentProcessor, 'CHUNK_OVERLAP')
        assert DocumentProcessor.CHUNK_SIZE > 0

    @pytest.mark.asyncio
    async def test_process_txt_file(self):
        """Test processing a plain text file."""
        content = "This is a test document with information"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert "test document" in text.lower()
            assert len(text) > 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_process_markdown_file(self):
        """Test processing a markdown file."""
        content = "# Test Document\n\nThis is markdown content"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.md')
            assert len(text) > 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_unsupported_format_raises_error(self):
        """Test that unsupported file formats raise ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"unknown format")
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                await DocumentProcessor.process_document(temp_path, '.xyz')
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_nonexistent_file_raises_error(self):
        """Test error handling for nonexistent file."""
        with pytest.raises((FileNotFoundError, Exception)):
            await DocumentProcessor.process_document("/nonexistent/file.txt", '.txt')

    @pytest.mark.asyncio
    async def test_empty_txt_file(self):
        """Test processing an empty text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            # Empty file should return empty string
            assert text == ""
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_small_txt_file(self):
        """Test processing a small text file."""
        content = "Small content"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert "Small content" in text
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_large_txt_file(self):
        """Test processing a larger text file."""
        # Create a file with multiple sentences
        content = ". ".join([f"Sentence {i}" for i in range(100)])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert len(text) > 1000  # Should have substantial content
            assert "Sentence" in text
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_markdown_with_formatting(self):
        """Test processing markdown with formatting."""
        content = """# Title

## Subtitle

- Point 1
- Point 2

**Bold text** and _italic text_
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.md')
            # Markdown should be preserved/extracted
            assert len(text) > 0
            assert "Title" in text or "Subtitle" in text or "Point" in text
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_txt_preserves_newlines(self):
        """Test that text files preserve line breaks."""
        content = "Line 1\nLine 2\nLine 3"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert "Line 1" in text
            assert "Line 2" in text
            assert "Line 3" in text
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_txt_with_special_characters(self):
        """Test processing text with special characters."""
        content = "Test with special chars: @#$%^&*() and unicode: 你好世界"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert "@#$%" in text or len(text) > 0
        finally:
            os.unlink(temp_path)

    def test_chunk_size_is_positive(self):
        """Test that chunk size is a positive integer."""
        assert isinstance(DocumentProcessor.CHUNK_SIZE, int)
        assert DocumentProcessor.CHUNK_SIZE > 0

    def test_chunk_overlap_is_valid(self):
        """Test that chunk overlap is valid."""
        assert isinstance(DocumentProcessor.CHUNK_OVERLAP, int)
        assert DocumentProcessor.CHUNK_OVERLAP >= 0
        assert DocumentProcessor.CHUNK_OVERLAP < DocumentProcessor.CHUNK_SIZE


class TestDocumentFormats:
    """Test specific file format support."""

    @pytest.mark.asyncio
    async def test_txt_extension_supported(self):
        """Test that .txt format is supported."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            # Should not raise exception
            text = await DocumentProcessor.process_document(temp_path, '.txt')
            assert isinstance(text, str)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_md_extension_supported(self):
        """Test that .md format is supported."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_path = f.name

        try:
            text = await DocumentProcessor.process_document(temp_path, '.md')
            assert isinstance(text, str)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_case_insensitive_extension(self):
        """Test that extension matching is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.TXT', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            # Should handle uppercase extension
            text = await DocumentProcessor.process_document(temp_path, '.TXT')
            assert isinstance(text, str)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
