"""
Format document chunks for inclusion in LLM system prompt.

Converts database DocumentChunk objects into human-readable context
suitable for LangChain system prompts.
"""

from db.models import DocumentChunk
from collections import defaultdict


def format_chunks_for_context(chunks: list[DocumentChunk]) -> str:
    """
    Format document chunks into markdown string for system prompt.

    Groups chunks by source document and provides context about where
    information comes from.

    Args:
        chunks: List of DocumentChunk objects from vector search

    Returns:
        Formatted markdown string suitable for system prompt, or empty string

    Example Output:
        ## Relevant Documents

        **Source: resume.pdf** (Chunks 1-3)
        - Senior engineer with 10+ years experience
        - Expertise in Python, Go, and cloud infrastructure
        - Led teams of 8+ engineers

        **Source: portfolio.md** (Chunks 4-6)
        - Built 5 production systems with RAG
        - Speaker at 3 major tech conferences
        - Open-source contributor with 500+ GitHub stars

        Use this information to provide context-aware responses. If the
        retrieved documents don't answer the question, inform the user.
    """
    if not chunks:
        return ""

    # Group chunks by source document (source_id is the document UUID)
    chunks_by_source = defaultdict(list)
    source_filenames = {}

    for chunk in chunks:
        chunks_by_source[str(chunk.source_id)].append(chunk)

    # Try to get filenames for documents (if source_type is 'document')
    # For now, just use generic naming since we don't have document objects
    for i, source_id in enumerate(chunks_by_source.keys(), 1):
        # Look at first chunk to determine source type
        first_chunk = chunks_by_source[source_id][0]
        if first_chunk.source_type == 'document':
            source_filenames[source_id] = f"Document {i}"
        elif first_chunk.source_type == 'fact':
            source_filenames[source_id] = "Stored Facts"
        else:
            source_filenames[source_id] = f"Source {i}"

    # Build formatted output
    lines = ["## Relevant Information from Your Documents\n"]

    chunk_num = 1
    for source_id, source_chunks in chunks_by_source.items():
        filename = source_filenames[source_id]
        end_chunk_num = chunk_num + len(source_chunks) - 1

        lines.append(f"**{filename}** (Chunks {chunk_num}-{end_chunk_num})")

        # Add chunk content previews (first 100 chars of each chunk)
        for chunk in source_chunks:
            preview = chunk.content[:100].strip()
            if len(chunk.content) > 100:
                preview += "..."
            lines.append(f"- {preview}")

        lines.append("")  # Blank line between sources
        chunk_num = end_chunk_num + 1

    # Add instruction for using context
    lines.append(
        "Use this information to provide accurate, context-aware responses. "
        "If the documents don't contain relevant information, inform the user."
    )
    lines.append("")

    return "\n".join(lines)


def format_chunks_for_citation(chunks: list[DocumentChunk]) -> str:
    """
    Format chunks for citation in bot responses.

    Returns a list of document sources that were used in the response,
    suitable for adding at the end of a message like "(Sources: doc1, doc2)".

    Args:
        chunks: List of DocumentChunk objects

    Returns:
        Citation string or empty string

    Example: "(Based on: resume.pdf, portfolio.md)"
    """
    if not chunks:
        return ""

    # Group unique sources
    sources = set()
    for chunk in chunks:
        if chunk.source_type == 'document':
            sources.add(f"Document {chunk.source_id}")

    if not sources:
        return ""

    source_list = ", ".join(sorted(sources))
    return f"(Based on: {source_list})"
