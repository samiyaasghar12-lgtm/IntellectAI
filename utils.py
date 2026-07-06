import os
import json
import base64
from datetime import datetime
from html.parser import HTMLParser

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False

try:
    import PyPDF2
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False

try:
    import docx
    _HAS_DOCX = True
except Exception:
    _HAS_DOCX = False

MEMORY_FILE = "chat_memory.json"
PROFILE_FILE = "profile.json"

DEFAULT_PROFILE = {
    "name": "Samiya Asghar",
    "first_name": "",
    "last_name": "",
    "program": "BS",
    "department": "Computer Science and Software Engineering",
    "year": "2025-2029",
    "status": "Undergraduate Student",
    "university": "Jinnah University for Women",
    "matriculation": "",
    "intermediate": "",
    "certifications": "",
    "contact": "",
    "address": "",
    "skills": "",
    "experience": "",
}


def image_data_uri(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None


def load_profile(profile_file=None):
    pf = profile_file or PROFILE_FILE
    default_profile = dict(DEFAULT_PROFILE)
    if os.path.exists(pf):
        try:
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_profile.update(data)
                return default_profile
        except Exception:
            return default_profile
    return default_profile


def save_profile(profile_data, profile_file=None):
    pf = profile_file or PROFILE_FILE
    try:
        with open(pf, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_memory(memory_file=None):
    mf = memory_file or MEMORY_FILE
    if os.path.exists(mf):
        try:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            return []
    return []


def save_memory(data, memory_file=None):
    mf = memory_file or MEMORY_FILE
    try:
        with open(mf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def fetch_url_text(url):
    if not _HAS_REQUESTS:
        return f"[Link saved: {url}] (install 'requests' to import page text)"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        parser = _TextExtractor()
        parser.feed(resp.text)
        text = " ".join(parser.parts)
        return text[:8000]
    except Exception as e:
        return f"[Could not load {url}: {e}]"


def extract_file_text(file_path=None, uploaded_file=None, file_name=""):
    name = file_name or (os.path.basename(file_path) if file_path else "file")
    lower = name.lower()
    try:
        if lower.endswith(".pdf") and _HAS_PYPDF2:
            reader = PyPDF2.PdfReader(file_path if file_path else uploaded_file)
            return "\n".join((p.extract_text() or "") for p in reader.pages)[:8000]
        if lower.endswith(".docx") and _HAS_DOCX:
            d = docx.Document(file_path if file_path else uploaded_file)
            return "\n".join(p.text for p in d.paragraphs)[:8000]
        if file_path:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:8000]
        if uploaded_file is not None:
            return uploaded_file.read().decode("utf-8", errors="ignore")[:8000]
    except Exception as e:
        return f"[Could not read {name}: {e}]"
    return f"[Saved source: {name}]"


def build_chat_entry(messages, current_id=None):
    if not messages:
        return None
    first_user_msg = next(
        (m["content"] for m in messages if m["role"] == "user"), "New Chat"
    )
    title = (first_user_msg[:30] + "...") if len(first_user_msg) > 30 else first_user_msg
    entry_id = current_id or datetime.now().isoformat()
    return {
        "id": entry_id,
        "title": title,
        "messages": messages,
        "ts": datetime.now().strftime("%I:%M %p"),
    }


def update_chat_list(all_chats, entry):
    updated = [c for c in all_chats if c["id"] != entry["id"]]
    updated.insert(0, entry)
    return updated
