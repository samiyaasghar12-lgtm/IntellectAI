import io
import json
import os
import tempfile
from unittest import mock

import pytest

from utils import (
    _TextExtractor,
    build_chat_entry,
    extract_file_text,
    fetch_url_text,
    image_data_uri,
    load_memory,
    load_profile,
    save_memory,
    save_profile,
    update_chat_list,
    DEFAULT_PROFILE,
)


# ---------------------------------------------------------------------------
# image_data_uri
# ---------------------------------------------------------------------------

class TestImageDataUri:
    def test_returns_data_uri_for_valid_file(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        result = image_data_uri(str(img))
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_returns_none_for_nonexistent_file(self):
        assert image_data_uri("/no/such/file.png") is None

    def test_returns_none_for_directory(self, tmp_path):
        assert image_data_uri(str(tmp_path)) is None

    def test_returns_none_for_unreadable_path(self, tmp_path):
        f = tmp_path / "locked.png"
        f.write_bytes(b"data")
        f.chmod(0o000)
        result = image_data_uri(str(f))
        # Should return None because reading fails
        f.chmod(0o644)  # restore so cleanup works
        assert result is None


# ---------------------------------------------------------------------------
# load_profile / save_profile
# ---------------------------------------------------------------------------

class TestProfile:
    def test_load_default_when_no_file(self, tmp_path):
        profile = load_profile(str(tmp_path / "missing.json"))
        assert profile == DEFAULT_PROFILE

    def test_save_and_load_roundtrip(self, tmp_path):
        pf = str(tmp_path / "profile.json")
        data = {"name": "Test User", "program": "MS"}
        save_profile(data, pf)
        loaded = load_profile(pf)
        assert loaded["name"] == "Test User"
        assert loaded["program"] == "MS"
        # Defaults should still be present for unset keys
        assert loaded["university"] == DEFAULT_PROFILE["university"]

    def test_load_handles_corrupt_json(self, tmp_path):
        pf = tmp_path / "profile.json"
        pf.write_text("{bad json", encoding="utf-8")
        profile = load_profile(str(pf))
        assert profile == DEFAULT_PROFILE

    def test_save_creates_file(self, tmp_path):
        pf = str(tmp_path / "new_profile.json")
        save_profile({"name": "Alice"}, pf)
        assert os.path.exists(pf)
        with open(pf, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["name"] == "Alice"

    def test_save_handles_write_error(self, tmp_path):
        # Writing to a directory path should not raise
        save_profile({"name": "fail"}, str(tmp_path))


# ---------------------------------------------------------------------------
# load_memory / save_memory
# ---------------------------------------------------------------------------

class TestMemory:
    def test_load_empty_when_no_file(self, tmp_path):
        result = load_memory(str(tmp_path / "nope.json"))
        assert result == []

    def test_save_and_load_roundtrip(self, tmp_path):
        mf = str(tmp_path / "memory.json")
        data = [{"id": "1", "title": "Chat 1", "messages": []}]
        save_memory(data, mf)
        loaded = load_memory(mf)
        assert loaded == data

    def test_load_returns_empty_for_non_list(self, tmp_path):
        mf = tmp_path / "memory.json"
        mf.write_text('{"not": "a list"}', encoding="utf-8")
        result = load_memory(str(mf))
        assert result == []

    def test_load_handles_corrupt_json(self, tmp_path):
        mf = tmp_path / "memory.json"
        mf.write_text("not json at all", encoding="utf-8")
        result = load_memory(str(mf))
        assert result == []

    def test_save_handles_write_error(self, tmp_path):
        save_memory([1, 2], str(tmp_path))


# ---------------------------------------------------------------------------
# _TextExtractor
# ---------------------------------------------------------------------------

class TestTextExtractor:
    def test_extracts_plain_text(self):
        parser = _TextExtractor()
        parser.feed("<p>Hello World</p>")
        assert parser.parts == ["Hello World"]

    def test_skips_script_content(self):
        parser = _TextExtractor()
        parser.feed("<div>Visible</div><script>hidden()</script><p>Also visible</p>")
        assert "Visible" in parser.parts
        assert "Also visible" in parser.parts
        assert "hidden()" not in parser.parts

    def test_skips_style_content(self):
        parser = _TextExtractor()
        parser.feed("<style>.cls{color:red}</style><span>Text</span>")
        assert parser.parts == ["Text"]

    def test_strips_whitespace(self):
        parser = _TextExtractor()
        parser.feed("<p>  \n  </p><p>Real text</p>")
        assert parser.parts == ["Real text"]

    def test_empty_html(self):
        parser = _TextExtractor()
        parser.feed("")
        assert parser.parts == []

    def test_nested_tags(self):
        parser = _TextExtractor()
        parser.feed("<div><p>A</p><p>B</p></div>")
        assert parser.parts == ["A", "B"]

    def test_multiple_scripts_and_styles(self):
        parser = _TextExtractor()
        html = (
            "<script>a()</script>"
            "<p>Keep</p>"
            "<style>b{}</style>"
            "<script>c()</script>"
            "<span>Me</span>"
        )
        parser.feed(html)
        assert parser.parts == ["Keep", "Me"]


# ---------------------------------------------------------------------------
# fetch_url_text
# ---------------------------------------------------------------------------

class TestFetchUrlText:
    def test_successful_fetch(self):
        fake_response = mock.Mock()
        fake_response.text = "<html><body><p>Hello fetch</p></body></html>"
        with mock.patch("utils._HAS_REQUESTS", True), \
             mock.patch("utils.requests.get", return_value=fake_response):
            result = fetch_url_text("https://example.com")
        assert "Hello fetch" in result

    def test_network_error(self):
        with mock.patch("utils._HAS_REQUESTS", True), \
             mock.patch("utils.requests.get", side_effect=Exception("timeout")):
            result = fetch_url_text("https://example.com")
        assert "[Could not load" in result

    def test_no_requests_library(self):
        with mock.patch("utils._HAS_REQUESTS", False):
            result = fetch_url_text("https://example.com")
        assert "[Link saved:" in result
        assert "install 'requests'" in result

    def test_truncates_to_8000_chars(self):
        long_text = "A" * 10000
        fake_response = mock.Mock()
        fake_response.text = f"<p>{long_text}</p>"
        with mock.patch("utils._HAS_REQUESTS", True), \
             mock.patch("utils.requests.get", return_value=fake_response):
            result = fetch_url_text("https://example.com")
        assert len(result) <= 8000


# ---------------------------------------------------------------------------
# extract_file_text
# ---------------------------------------------------------------------------

class TestExtractFileText:
    def test_extract_plain_text_file(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Hello from text file", encoding="utf-8")
        result = extract_file_text(file_path=str(f), file_name="notes.txt")
        assert result == "Hello from text file"

    def test_extract_from_uploaded_file(self):
        content = b"uploaded content"
        uploaded = io.BytesIO(content)
        result = extract_file_text(uploaded_file=uploaded, file_name="up.txt")
        assert result == "uploaded content"

    def test_truncates_long_files(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_text("X" * 10000, encoding="utf-8")
        result = extract_file_text(file_path=str(f), file_name="big.txt")
        assert len(result) == 8000

    def test_fallback_for_unknown_type_no_file(self):
        result = extract_file_text(file_name="archive.zip")
        assert "[Saved source:" in result

    def test_uses_basename_when_no_file_name(self, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("# Title", encoding="utf-8")
        result = extract_file_text(file_path=str(f))
        assert "# Title" in result

    def test_handles_read_error(self):
        result = extract_file_text(file_path="/nonexistent/path.txt", file_name="path.txt")
        assert "[Could not read" in result

    def test_pdf_extraction_with_mock(self, tmp_path):
        mock_page = mock.Mock()
        mock_page.extract_text.return_value = "PDF page text"
        mock_reader = mock.Mock()
        mock_reader.pages = [mock_page]
        with mock.patch("utils._HAS_PYPDF2", True), \
             mock.patch("utils.PyPDF2.PdfReader", return_value=mock_reader):
            result = extract_file_text(file_path="/fake/doc.pdf", file_name="doc.pdf")
        assert result == "PDF page text"

    def test_docx_extraction_with_mock(self):
        mock_para1 = mock.Mock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = mock.Mock()
        mock_para2.text = "Paragraph 2"
        mock_doc = mock.Mock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        with mock.patch("utils._HAS_DOCX", True), \
             mock.patch("utils.docx.Document", return_value=mock_doc):
            result = extract_file_text(file_path="/fake/doc.docx", file_name="doc.docx")
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result


# ---------------------------------------------------------------------------
# build_chat_entry
# ---------------------------------------------------------------------------

class TestBuildChatEntry:
    def test_returns_none_for_empty_messages(self):
        assert build_chat_entry([]) is None
        assert build_chat_entry(None) is None

    def test_builds_entry_with_user_message(self):
        msgs = [{"role": "user", "content": "What career path?"}]
        entry = build_chat_entry(msgs, current_id="abc123")
        assert entry["id"] == "abc123"
        assert entry["title"] == "What career path?"
        assert entry["messages"] == msgs
        assert "ts" in entry

    def test_truncates_long_titles(self):
        long_msg = "A" * 50
        msgs = [{"role": "user", "content": long_msg}]
        entry = build_chat_entry(msgs)
        assert entry["title"] == long_msg[:30] + "..."

    def test_defaults_title_when_no_user_message(self):
        msgs = [{"role": "assistant", "content": "Hello!"}]
        entry = build_chat_entry(msgs)
        assert entry["title"] == "New Chat"

    def test_auto_generates_id_when_none(self):
        msgs = [{"role": "user", "content": "Hi"}]
        entry = build_chat_entry(msgs, current_id=None)
        assert entry["id"] is not None
        assert len(entry["id"]) > 0


# ---------------------------------------------------------------------------
# update_chat_list
# ---------------------------------------------------------------------------

class TestUpdateChatList:
    def test_inserts_new_entry_at_front(self):
        existing = [{"id": "old", "title": "Old"}]
        new_entry = {"id": "new", "title": "New"}
        result = update_chat_list(existing, new_entry)
        assert result[0]["id"] == "new"
        assert result[1]["id"] == "old"

    def test_replaces_existing_entry(self):
        existing = [
            {"id": "a", "title": "A"},
            {"id": "b", "title": "B"},
        ]
        updated = {"id": "b", "title": "B updated"}
        result = update_chat_list(existing, updated)
        assert len(result) == 2
        assert result[0]["id"] == "b"
        assert result[0]["title"] == "B updated"
        assert result[1]["id"] == "a"

    def test_empty_list(self):
        result = update_chat_list([], {"id": "x", "title": "X"})
        assert len(result) == 1
        assert result[0]["id"] == "x"

    def test_preserves_other_entries(self):
        existing = [
            {"id": "1", "title": "First"},
            {"id": "2", "title": "Second"},
            {"id": "3", "title": "Third"},
        ]
        updated = {"id": "2", "title": "Updated Second"}
        result = update_chat_list(existing, updated)
        assert len(result) == 3
        ids = [c["id"] for c in result]
        assert ids == ["2", "1", "3"]
