"""Shared utilities for IntellectAI (edu-career-ai-agent).

These helpers centralize patterns that were previously duplicated across
``agent.py`` (JSON persistence, image encoding, Gemini model setup, and the
mobile clipboard-paste button rendered inside dialogs).
"""
import os
import json
import base64

import google.generativeai as genai


def read_json_file(path, default):
    """Return the JSON content of ``path`` or ``default`` if it is missing/unreadable."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json_file(path, data):
    """Write ``data`` to ``path`` as pretty UTF-8 JSON, swallowing IO errors."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def image_data_uri(path):
    """Return a base64 ``data:`` URI for the image at ``path`` or ``None``."""
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None


def get_gemini_model(api_key, model_name):
    """Configure the Gemini client and return a model instance."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def clipboard_paste_button_html(button_id, param_name, label):
    """Build the HTML/JS for the mobile "paste from clipboard" button.

    The button reads the clipboard and reloads the parent page with the pasted
    value stored in the ``param_name`` query parameter.
    """
    return f"""
    <button id="{button_id}" style="
        background-color: #2b2b40;
        color: #ffffff;
        border: 1px solid #3e3e5c;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
        font-family: system-ui, sans-serif;
        width: 100%;
        cursor: pointer;
        margin-bottom: 12px;
        font-weight: 600;
    ">{label}</button>
    <script>
        document.getElementById('{button_id}').addEventListener('click', async () => {{
            try {{
                const text = await navigator.clipboard.readText();
                const url = new URL(window.parent.location.href);
                url.searchParams.set('{param_name}', text);
                window.parent.location.href = url.href;
            }} catch (err) {{
                alert('Please allow clipboard access or paste manually.');
            }}
        }});
    </script>
    """
