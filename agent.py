import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from utils import (
    read_json_file,
    write_json_file,
    image_data_uri,
    get_gemini_model,
    clipboard_paste_button_html,
)
try:
    import requests
    from html.parser import HTMLParser
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
load_dotenv()
st.set_page_config(
    page_title="IntellectAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
MEMORY_FILE = "chat_memory.json"
PROFILE_FILE = "profile.json"
ROBOT_FILE = "robot.png"
PROFILE_PIC_FILE = "profile_pic.png"
ROBOT_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBWrVbKZGdXiQ4iDQu-amwsD7Vy8e1q8ng_MuTpsneIw&s=10"
PROFILE_PIC_B64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAJQAsgMBIgACEQEDEQH/xAAbAAEAAwEBAQEAAAAAAAAAAAAABAUGAwECB//EADgQAAIBAgIIBAIIBwEAAAAAAAABAgMEBRESFCExQVRxoRNRUmEiMkJDU4GRscHRIzNygpLw8RX/xAAVAQEBAAAAAAAAAAAAAAAAAAAAAf/EABYRAQEBAAAAAAAAAAAAAAAAAAABEf/aAAwDAQACEQMRAD8A/WwAVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPNnED08lJRjnNqMfNkK/xGNt/DgtKr5cI9Sjr16teWlVm5P3ZcF/PErSD21VL+lNnysVs3vqSX9jM8Bg1NKvSrfyqsZ9GdTJJuLzi2nwaeRZ2WKyhlC6znH18V1JgugeRakh4tOLWaae89AAAAAAAAAAAAAAAAAAAAQ8Su9VpfDl4k9kfb3JhmsQr6xd1JL5U9GPRCFR222229re9ngBUAAAABRZYReOlUVCo/gnsjnwZeGSNLYV9YtKdR/NllLqiUSAARQAAAAAAAAAAAAAAAHO4n4dCpPjGLZleBp75Z2VfL0MzBYlAAAAAAAAC5wGedOrT8mn/AL+BTFtgC+Ks/aP6gXAAIoAAAAAAAAAAAAAAAD5qQ06coPisjKSi4ycXvWxmtKHGLfwrjxF8tTb9/EQV4AKgAAAAAF5gdNxtpzf05fkimpU5VakYQWcpPI09CkqFGFKO6MUl7jVdAAQAAAAAAAAAAAAAAAADlc0I3NGVKo8k9z8vc6gDLXFvUtqjhUWW3Y+DRyNTcUKVxDQqxzjw80U9zhNaDboPxF6dzKK4HSdGrTeU6cov3iz5UJN5KMn0QR8nq25LiyVQw65rPZDQj6p7C3s8PpWzU38dT1NbF0GuWF2PgLxaqfiS3L0osQCAAAAAAAAAAAAAAAAAAQ7zEaVs3HLTqL6MXu6sCYR617b0M1Oom1wjtZR3N9cXGanNxh6YPYRS4mrmpjUE8qVGUveTyI0sYuJP4VTj0WZXgCY8UvH9al0igsSu08/FX+C/YhgKnwxa6jv0H1id6eNS+so5rzjL9yqARoKOKWtXfN035TWRMi1KOcWmvNPYZI60a9WhLSozlF+WewYa1IKu0xeMso3K0X647n+xZpqSTi8092RFegAAAAAAAAAAPvBUYvevN21J7PrGvyA+cQxNycqNtLKO5zXHoVQBQAAQAAAAAAAAAAAl2V7UtZb9Om98H+hEAVqqNWFamp0nnF9joZuwu5WtXPa6cvnX6mji1KKlF5prNPzIPQAAAAAAAcbyvq1vOrxS+Fe/AzDbbbbzb3suMem1GjTXFuX4f9KYsKAAIAAAAAAAAAAAAAAAAF1glfTpyoSe2G1dGUpLwuo6d9TyfzPRfvmKsaMAEAAAAABwuLajXadampNbE2c//PtPsI9wCwNQtOXh3GoWn2Ee4ADULTl49xqFpy8e4ADULTl49xqFpy8e4ADULTl49xqFpy8e4ADULTl49z6p2NrGcZRoRTi809u9AASfMAEAAAf/2Q=="
_env_key = os.getenv("GEMINI_API_KEY", "")
try:
    _secrets_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    _secrets_key = ""
API_KEY = (_secrets_key or _env_key or "").strip()
MODELS = ["gemini-1.5-pro", "gemini-pro"]
ROBOT_URI = image_data_uri(ROBOT_FILE) or ROBOT_URL
PROFILE_PIC_URI = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrvqMr_iJ5proxfjDhFMCRPVIBwUyZXvdHN68lgwo0gA&s=10"
SYSTEM_PROMPT = """You are "IntellectAI", a dedicated personalized Education & Career advisor.
Your one and only purpose is to guide students toward a better academic life, career, and future.
============================
LANGUAGE RULES (VERY IMPORTANT)
============================
- Detect the language of the user's message and ALWAYS reply in the SAME language:
  - If the user writes in English  -> reply in English.
  - If the user writes in Urdu (Urdu script) -> reply in Urdu (Urdu script).
  - If the user writes in Roman Urdu / Roman English -> reply in Roman Urdu.
- Never switch the language unless the user switches first.
============================
SCOPE (STRICT)
============================
- You ONLY answer questions related to EDUCATION, study, academics, careers, fields,
  domains, university subjects, exams, interviews, tests, notes, roadmaps, future
  guidance, and dictionary/word meanings.
- If a question is OUTSIDE the education/career context (e.g. politics, gossip, jokes,
  cooking, random chit-chat, anything unrelated to learning or careers), politely REFUSE
  in the user's language.
- Keep the refusal short and respectful.
============================
WHAT YOU CAN DO
============================
- Career guidance, future planning, roadmaps, phases, steps, and field/domain guides.
- Dictionary feature: give meaning/definition of any word in English, Urdu, or Roman Urdu.
- Help with university notes, summaries, assignment understanding, and study help.
- Interview preparation and test/exam preparation.
- Generate quizzes, model answers, and study plans.
Always be encouraging, supportive, and focused on the student's growth and future success."""
def load_profile():
    default_profile = {
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
    data = read_json_file(PROFILE_FILE, None)
    if isinstance(data, dict):
        default_profile.update(data)
    return default_profile
def save_profile(profile_data):
    write_json_file(PROFILE_FILE, profile_data)
def load_memory():
    data = read_json_file(MEMORY_FILE, [])
    return data if isinstance(data, list) else []
def save_memory(data):
    write_json_file(MEMORY_FILE, data)
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "file_context" not in st.session_state:
    st.session_state.file_context = ""
if "view_state" not in st.session_state:
    st.session_state.view_state = "chat"
if "sources" not in st.session_state:
    st.session_state.sources = []
if "profile_editing" not in st.session_state:
    st.session_state.profile_editing = False
def new_chat():
    st.session_state.messages = []
    st.session_state.current_id = None
    st.session_state.file_context = ""
    st.session_state.sources = []
    st.session_state.view_state = "chat"
def persist_current():
    if not st.session_state.messages:
        return
    first_user_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "New Chat")
    title = (first_user_msg[:30] + "...") if len(first_user_msg) > 30 else first_user_msg
    entry_id = st.session_state.current_id or datetime.now().isoformat()
    entry = {
        "id": entry_id,
        "title": title,
        "messages": st.session_state.messages,
        "ts": datetime.now().strftime("%I:%M %p"),
    }
    st.session_state.current_id = entry_id
    updated_chats = [c for c in st.session_state.all_chats if c["id"] != entry_id]
    updated_chats.insert(0, entry)
    st.session_state.all_chats = updated_chats
    save_memory(updated_chats)
def load_chat(cid):
    for c in st.session_state.all_chats:
        if c["id"] == cid:
            st.session_state.messages = c["messages"]
            st.session_state.current_id = cid
            st.session_state.view_state = "chat"
            return
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

def add_source(icon, name, content):
    st.session_state.sources.append({"type": icon, "name": name, "content": content})

def ask_gemini(user_text):
    # Ye 2 lines add karein taake function ke andar key mil jaye
    global API_KEY 
    api_key = API_KEY if 'API_KEY' in globals() else st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        return "❌ Error: API Key missing."
    
    try:
        # History setup
        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        # Context setup
        payload_text = user_text
        if st.session_state.sources:
            active_context = "\n\n".join(s.get("content", "") for s in st.session_state.sources if s.get("content"))
            if active_context:
                payload_text = f"[CONTEXT]\n{active_context}\n\n[USER INQUIRY]\n{user_text}"
        
        history.append({"role": "user", "parts": [payload_text]})

        model = get_gemini_model(api_key, "gemini-2.5-flash")
        resp = model.generate_content(history)
        return resp.text
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def transcribe_audio(audio_bytes, mime_type="audio/wav"):
    if not API_KEY or API_KEY in ("your_new_api_key_here", ""):
        return ""
    try:
        model = get_gemini_model(API_KEY, "gemini-1.5-flash")
        resp = model.generate_content([
            "Transcribe this audio to plain text exactly as spoken. Keep the same language the speaker used. Return only the transcription.",
            {"mime_type": mime_type, "data": audio_bytes}
        ])
        return (resp.text or "").strip()
    except Exception:
        return ""

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #f8f9fc !important;
    }
    
    /* Override primary theme colors to completely remove Streamlit orange styling */
    html, body, [data-testid="stAppViewContainer"] {
        --primary-color: #8b5cf6 !important;
    }
    
    .main .block-container, div[data-testid="stAppViewBlockContainer"] {
        max-width: 820px !important;
        margin: 0 auto !important;
        padding-top: 4rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        display: flex !important;
        flex-direction: column !important;
    }
    section[data-testid="stSidebar"] {
        background: #1c1c2e !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 24px 16px !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
        gap: 0;
    }
    .sb-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 20px 4px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
    }
    .sb-logo {
        width: 38px; height: 38px;
        border-radius: 10px;
        object-fit: cover;
        flex-shrink: 0;
    }
    .sb-title {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.3px;
        line-height: 1.1;
    }
    .sb-tagline {
        font-size: 11px !important;
        color: #8b8fa8 !important;
        font-weight: 400;
        letter-spacing: 0.2px;
    }
    .sb-profile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 16px;
        background: rgba(255,255,255,0.05);
    }
    .sb-avatar {
        width: 40px; height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid rgba(139,92,246,0.6);
        flex-shrink: 0;
    }
    .sb-uname {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #f3f4f6 !important;
        line-height: 1.2;
    }
    .sb-ustatus {
        font-size: 11px !important;
        color: #8b8fa8 !important;
        font-weight: 400;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        width: 100% !important;
        min-height: 48px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button span {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
        transform: translateX(2px);
    }
    .hero-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center !important;
        width: 100%;
        margin: 0 auto;
    }
    .hero-robot-img {
        width: 150px !important;
        height: 150px !important;
        object-fit: contain !important;
        margin: 20px auto 24px auto !important;
        display: block !important;
        border: none !important;
        background: transparent !important;
        filter: drop-shadow(0 10px 25px rgba(28,28,46,0.12));
    }
    .hero-title-main {
        font-size: 48px !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px !important;
        line-height: 1.2 !important;
        color: #1e293b !important;
        text-align: center !important;
        margin: 24px auto 16px auto !important;
        display: block !important;
    }
    .hero-sub-main {
        font-size: 18px !important;
        color: #475569 !important;
        background: transparent !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        max-width: 650px !important;
        margin: 0 auto 36px auto !important;
        text-align: center !important;
        display: block !important;
    }
    .disclaimer-text {
        font-family: 'Inter', sans-serif;
        font-size: clamp(12px, 1vw, 13.5px) !important;
        color: #7b8494 !important;
        text-align: center !important;
        max-width: 600px !important;
        margin: 0 auto 24px auto !important;
        line-height: 1.5 !important;
        display: block !important;
    }
    div[data-testid="stHorizontalBlock"] {
        max-width: 650px !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        gap: 12px !important;
    }
    
    /* Task 2: Style all buttons in the main chat area to match sidebar aesthetic */
    div[data-testid="stMain"] button, 
    div[data-testid="stMain"] div[data-testid="stButton"] > button,
    div[data-testid="stMain"] div[data-testid="stFormSubmitButton"] > button {
        background-color: #2b2b40 !important;
        color: #ffffff !important;
        border: 1px solid #3e3e5c !important;
        border-radius: 24px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease-in-out !important;
        white-space: nowrap !important;
    }
    div[data-testid="stMain"] button:hover,
    div[data-testid="stMain"] div[data-testid="stButton"] > button:hover,
    div[data-testid="stMain"] div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #383854 !important;
        border-color: #4f4f75 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMain"] button:active,
    div[data-testid="stMain"] button:focus {
        background-color: #1f1f2e !important;
        border-color: #2b2b40 !important;
        color: #ffffff !important;
    }
    
    div[data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        padding-bottom: 24px !important;
    }
    div[data-testid="stBottomBlockContainer"] > div {
        max-width: 760px !important;
        margin: 0 auto !important;
        padding: 0 12px !important;
    }
    div[data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 28px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        padding: 6px 12px 6px 20px !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        color: #1a1a2e !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15.5px !important;
    }
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #1c1c2e !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        border: none !important;
    }
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin: 12px 0 !important;
        border: 1px solid #eaecf0 !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
    }

    /* Strict mobile styling overrides */
    @media screen and (max-width: 600px) {
        .main .block-container, div[data-testid="stAppViewBlockContainer"] {
            padding-top: 10px !important;
            height: 85vh !important;
            overflow-y: hidden !important;
        }
        .hero-robot-img {
            width: 80px !important;
            height: 80px !important;
            margin: 10px auto !important;
        }
        .hero-title-main {
            font-size: 22px !important;
        }
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 10px !important;
            width: 90% !important;
            left: 5% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Silent background user agent & responsive mobile parameter checking setup
st.components.v1.html("""
<iframe src="javascript:void(0)" style="display:none" onload="
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    const url = new URL(parent.window.location.href);
    if (isMobile && url.searchParams.get('mobile') !== 'true') {
        url.searchParams.set('mobile', 'true');
        parent.window.location.href = url.href;
    } else if (!isMobile && url.searchParams.get('mobile') === 'true') {
        url.searchParams.delete('mobile');
        parent.window.location.href = url.href;
    }
"></iframe>
""", height=0)

current_profile = load_profile()

@st.dialog("Paste website & YouTube URLs to add as a source in IntellectAI")
def websites_dialog():
    is_mobile = st.query_params.get("mobile", "false") == "true"
    st.caption("Paste any links below to import as study sources.")
    
    if is_mobile:
        st.info("📱 Mobile Mode Active: Tap below to paste links instantly from your clipboard.")
        st.components.v1.html(
            clipboard_paste_button_html("paste-btn", "pasted_link", "📋 Paste Link from Clipboard"),
            height=52,
        )
        
        pasted_link = st.query_params.get("pasted_link", "")
        if pasted_link:
            st.success(f"Successfully Pasted: {pasted_link}")
            
    default_text = st.query_params.get("pasted_link", "")
    links = st.text_area("Paste any links", value=default_text, height=180, placeholder="https://example.com\nhttps://youtube.com/watch?v=...")
    
    if st.button("Insert", type="primary", key="ins_links"):
        urls = [u.strip() for u in links.replace("\n", " ").split(" ") if u.strip()]
        for u in urls:
            text = fetch_url_text(u)
            add_source("🌐", u, f"[WEBSITE SOURCE: {u}]\n{text}")
        st.session_state.view_state = "chat"
        # Clean pasted parameter query context before reload
        if "pasted_link" in st.query_params:
            del st.query_params["pasted_link"]
        st.rerun()

@st.dialog("Upload files from your folder")
def upload_dialog():
    is_mobile = st.query_params.get("mobile", "false") == "true"
    st.caption("Choose files from your computer folder to add as study sources.")
    
    if is_mobile:
        st.info("📱 Mobile Mode Active: Trigger native file explorer/camera inputs dynamically below.")
        camera_file = st.camera_input("📸 Capture note details instantly using device camera")
        if camera_file:
            img_bytes = camera_file.read()
            add_source(
                "📄",
                f"camera_note_{datetime.now().strftime('%M%S')}.png",
                "[CAMERA CAPTURE NOTE: Captured dynamically on mobile]",
            )
            st.success("Camera snapshot appended!")
            
    files = st.file_uploader("Upload files", type=["pdf", "docx", "txt", "md", "py", "csv", "json"], accept_multiple_files=True, key="uploader_main")
    
    if st.button("Add as sources", type="primary", key="add_uploads"):
        for f in files or []:
            text = extract_file_text(uploaded_file=f, file_name=f.name)
            add_source("📄", f.name, f"[UPLOADED FILE: {f.name}]\n{text}")
        st.session_state.view_state = "chat"
        st.rerun()

@st.dialog("Select items")
def drive_dialog():
    is_mobile = st.query_params.get("mobile", "false") == "true"
    st.markdown("<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'><b style='font-size:18px;'>Search in Drive or paste URL</b></div>", unsafe_allow_html=True)
    
    if is_mobile:
        st.info("📱 Mobile Clipboard Assistant: Grab Drive link directly from clip storage.")
        st.components.v1.html(
            clipboard_paste_button_html("paste-drive-btn", "pasted_drive", "📋 Paste Drive Link"),
            height=52,
        )
        
        pasted_drive = st.query_params.get("pasted_drive", "")
        if pasted_drive:
            st.success(f"Drive Link Detected: {pasted_drive}")
            
    default_drive = st.query_params.get("pasted_drive", "")
    drive_url = st.text_input("Paste a Google Drive link", value=default_drive, key="drive_url_in")
    
    if st.button("Insert", type="primary", key="ins_drive"):
        if drive_url:
            text = fetch_url_text(drive_url)
            add_source("📁", drive_url, f"[DRIVE SOURCE: {drive_url}]\n{text}")
            st.session_state.view_state = "chat"
            if "pasted_drive" in st.query_params:
                del st.query_params["pasted_drive"]
            st.rerun()

with st.sidebar:
    _robot_html = f"<img src='{ROBOT_URI}' class='sb-logo'/>" if ROBOT_URI else "🤖"
    st.markdown(f"<div class='sb-brand'>{_robot_html}<div><div class='sb-title'>IntellectAI</div><div class='sb-tagline'>Education &amp; Career Advisor</div></div></div>", unsafe_allow_html=True)
    if PROFILE_PIC_URI:
        st.markdown(f"<div class='sb-profile'><img src='{PROFILE_PIC_URI}' class='sb-avatar'/><div><div class='sb-uname'>{current_profile['name']}</div><div class='sb-ustatus'>{current_profile['status']}</div></div></div>", unsafe_allow_html=True)
    if st.button("👤  My Profile", use_container_width=True):
        st.session_state.view_state = "profile"
        st.rerun()
    if st.button("💬  New Chat", use_container_width=True):
        persist_current()
        new_chat()
        st.rerun()
    if st.session_state.all_chats:
        for c in st.session_state.all_chats:
            if st.button(f"💬 {c['ts']} - {c['title']}", use_container_width=True):
                load_chat(c["id"])
                st.rerun()
    if st.button("⚙️  Settings", use_container_width=True):
        st.session_state.view_state = "settings"
        st.rerun()
if st.session_state.view_state == "profile":

    st.image(PROFILE_PIC_URI, width=120)

    st.title(current_profile["name"])
    st.caption(
        f"{current_profile['status']} · {current_profile['university']}"
    )

    if st.session_state.profile_editing:

        with st.form("profile_form"):

            name = st.text_input(
                "Full Name",
                current_profile.get("name", "")
            )

            first_name = st.text_input(
                "First Name",
                current_profile.get("first_name", "")
            )

            last_name = st.text_input(
                "Last Name",
                current_profile.get("last_name", "")
            )

            program = st.text_input(
                "Program",
                current_profile.get("program", "")
            )

            department = st.text_input(
                "Department",
                current_profile.get("department", "")
            )

            year = st.text_input(
                "Year",
                current_profile.get("year", "")
            )

            status = st.text_input(
                "Status",
                current_profile.get("status", "")
            )

            university = st.text_input(
                "University",
                current_profile.get("university", "")
            )

            matriculation = st.text_area(
                "Matriculation",
                current_profile.get("matriculation", "")
            )

            intermediate = st.text_area(
                "Intermediate",
                current_profile.get("intermediate", "")
            )

            certifications = st.text_area(
                "Certifications",
                current_profile.get("certifications", "")
            )

            contact = st.text_input(
                "Contact",
                current_profile.get("contact", "")
            )

            address = st.text_area(
                "Address",
                current_profile.get("address", "")
            )

            skills = st.text_area(
                "Skills",
                current_profile.get("skills", "")
            )

            experience = st.text_area(
                "Experience",
                current_profile.get("experience", "")
            )

            col1, col2 = st.columns(2)

            with col1:
                save_btn = st.form_submit_button("💾 Save")

            with col2:
                cancel_btn = st.form_submit_button("❌ Cancel")

            if save_btn:

                save_profile({
                    "name": name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "program": program,
                    "department": department,
                    "year": year,
                    "status": status,
                    "university": university,
                    "matriculation": matriculation,
                    "intermediate": intermediate,
                    "certifications": certifications,
                    "contact": contact,
                    "address": address,
                    "skills": skills,
                    "experience": experience
                })

                st.session_state.profile_editing = False
                st.rerun()

            if cancel_btn:
                st.session_state.profile_editing = False
                st.rerun()

    else:

        if st.button("✏️ Edit Profile"):
            st.session_state.profile_editing = True
            st.rerun()

        st.markdown("---")

        st.write("### Personal Information")
        st.write("First Name:", current_profile.get("first_name", ""))
        st.write("Last Name:", current_profile.get("last_name", ""))

        st.write("### Academic Information")
        st.write("Program:", current_profile.get("program", ""))
        st.write("Department:", current_profile.get("department", ""))
        st.write("Year:", current_profile.get("year", ""))
        st.write("Status:", current_profile.get("status", ""))
        st.write("University:", current_profile.get("university", ""))

        st.write("### Education")
        st.write("Matriculation:", current_profile.get("matriculation", ""))
        st.write("Intermediate:", current_profile.get("intermediate", ""))

        st.write("### Certifications")
        st.write(current_profile.get("certifications", ""))

        st.write("### Contact")
        st.write(current_profile.get("contact", ""))

        st.write("### Address")
        st.write(current_profile.get("address", ""))

        st.write("### Skills")
        st.write(current_profile.get("skills", ""))

        st.write("### Experience")
        st.write(current_profile.get("experience", ""))

elif st.session_state.view_state == "settings":

    if st.button("Clear History"):
        st.session_state.all_chats = []
        save_memory([])
        new_chat()
        st.rerun()

else:

    if not st.session_state.messages:

        st.markdown(
            f"<div class='hero-wrapper'>"
            f"<img src='{ROBOT_URI}' class='hero-robot-img'/>"
            f"<div class='hero-title-main'>What's on your mind, {current_profile['name']}?</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    else:

        for m in st.session_state.messages:

            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    st.markdown(
        '<div class="disclaimer-text">IntellectAI can make mistakes.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📤 Upload", use_container_width=True):
            upload_dialog()

    with c2:
        if st.button("🌐 Web", use_container_width=True):
            websites_dialog()

    with c3:
        if st.button("📁 Drive", use_container_width=True):
            drive_dialog()

    submission = st.chat_input(
        "Ask about careers, academics..."
    )

    if submission:

        st.session_state.messages.append({
            "role": "user",
            "content": submission
        })

        with st.spinner("Thinking..."):
            response = ask_gemini(submission)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        persist_current()
        st.rerun()
