from app.ingest import clean_text, chunk_text


def test_clean_text():
    text = "Hello   world\n\nThis is   RAG."
    cleaned = clean_text(text)

    assert cleaned == "Hello world This is RAG."


def test_chunk_text_creates_multiple_chunks():
    text = " ".join(["word"] * 300)

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) > 1
    assert chunks[0]["chunk_id"] == 0
    assert "text" in chunks[0]
