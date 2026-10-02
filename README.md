---
title: IntellectAI
sdk: streamlit
app_file: agent.py
---

<h1 align="center">🎓 IntellectAI</h1>
<p align="center"><b>Edu-Career AI Agent</b><br>
Your personal AI-powered academic and career advisor, built to help you navigate your professional journey.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.37%2B-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-AI-4285F4?logo=google&logoColor=white" alt="Google Gemini"/>
</p>

<p align="center">
  <a href="https://lnkd.in/dP7PWTJY"><b>🚀 Try the Live Agent</b></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Built With](#built-with)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Run in GitHub Codespaces](#run-in-github-codespaces)
- [How It Works](#how-it-works)
- [Known Limitations](#known-limitations)
- [Security](#security)
- [Author](#author)

---

## Overview

**IntellectAI** is a personal AI agent that helps students and professionals navigate their academic and career paths. It gives personalized guidance on academic queries in **English, Urdu and Roman Urdu**, and works on both laptop and mobile screens.

It was built as a **"Career Architect"** to help users put what they have learned into practice, guided by one idea:

> *Learning is incomplete without implementation.*

Users can chat with the assistant, keep a student profile, reopen saved conversations and add their own study material (files and links) as context for the answers.

---

## Features

- 💬 **AI chat advisor:** career guidance, roadmaps, exam and interview preparation, study help and word meanings, powered by Google Gemini
- 🌍 **Language matching:** designed to reply in the user's language (English, Urdu or Roman Urdu) through the system prompt
- 🎯 **Education-only scope:** the system prompt keeps the assistant on education and career topics
- 📚 **Study sources:** add context from uploaded files (PDF, DOCX, TXT, MD, PY, CSV, JSON), public website links and Google Drive links
- 🗂️ **Persistent chat history:** conversations are saved in `chat_memory.json` and listed in the sidebar
- 👤 **Student profile:** editable profile with program, department, university, skills, experience, certifications and contact details
- 🎨 **Custom responsive UI:** custom HTML/CSS on top of Streamlit with a dark sidebar and a layout that adapts to laptop and mobile screens
- 📱 **Mobile-aware interface:** mobile detection, clipboard paste helper and a camera capture option in the upload dialog
- ⚙️ **Settings:** clear chat history

---

## Built With

- **Python**
- **Streamlit**
- **Google Gemini AI** (`google-generativeai`)
- **JSON** (chat memory and profile storage)

<details>
<summary><b>Dependencies</b> (<code>requirements.txt</code>)</summary>

```
streamlit>=1.37.0
google-generativeai>=0.8.3
python-dotenv>=1.0.0
requests>=2.31.0
PyPDF2>=3.0.0
python-docx>=1.1.0
```

</details>

---

## Project Structure

```
edu-career-agent/
├── agent.py                    # Main application
├── requirements.txt            # Python dependencies
├── .env                        # API key (private)
├── .gitignore                  # Git ignore rules
├── chat_memory.json            # Persistent chat history
├── robot.png                   # UI asset
├── README.md                   # Project documentation
├── .streamlit/
│   └── config.toml             # Theme and port configuration
└── .devcontainer/
    └── devcontainer.json       # GitHub Codespaces / dev container setup
```

`profile.json` is also created automatically when the student profile is saved.

---

## Getting Started

### Prerequisites

- Python 3.11 (the version used in the dev container)
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/edu-career-agent.git
cd edu-career-agent

# Install dependencies
pip install -r requirements.txt
```

### API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

The app also reads `GEMINI_API_KEY` from Streamlit secrets, which is useful for deployment.

### Run

```bash
streamlit run agent.py
```

The app opens on **http://localhost:8501**.

---

## Usage

1. Open the app and type a question about your studies or career in the chat box.
2. Use the **Upload**, **Web** or **Drive** buttons under the chat to add files or links as context.
3. Open **My Profile** in the sidebar to view or edit your student profile.
4. Use **New Chat** to start a fresh conversation, and pick earlier chats from the sidebar list.
5. Open **Settings** to clear your chat history.

---

## Configuration

Settings in `.streamlit/config.toml`:

| Section | Setting | Value |
|---------|---------|-------|
| `[server]` | `headless` | `false` |
| `[server]` | `port` | `8501` |
| `[browser]` | `gatherUsageStats` | `false` |
| `[theme]` | `primaryColor` | `#6C63FF` |
| `[theme]` | `backgroundColor` | `#FFFFFF` |
| `[theme]` | `secondaryBackgroundColor` | `#F8FAFC` |
| `[theme]` | `textColor` | `#0D1117` |

---

## Run in GitHub Codespaces

The `.devcontainer/devcontainer.json` file sets up a ready-to-use environment:

- Python 3.11 dev container with the Python and Pylance extensions
- Installs `requirements.txt` automatically
- Starts the app with `streamlit run agent.py`
- Forwards port **8501** and opens it as a preview

Open the repository in Codespaces, add your `GEMINI_API_KEY` as a Codespaces secret (or in a `.env` file), and the app starts on its own.

---

## How It Works

1. The user sends a message in the chat.
2. Any added sources (files or links) are attached to the prompt as context.
3. The chat history and context are sent to Google Gemini.
4. The reply is shown in the chat and the conversation is saved to `chat_memory.json`.

---

## Known Limitations

- Website and Drive import read only publicly accessible pages; private files need to be uploaded directly.
- A camera snapshot is added as a note placeholder; the image content is not analyzed yet.
- An audio transcription helper exists in the code but is not connected to the interface yet.
- Chat history and profile are stored in local JSON files, so there are no separate user accounts.

---

## Security

- The API key is read from `.env` or Streamlit secrets and is never written in the code.
- Keep `.env`, `chat_memory.json` and `profile.json` listed in `.gitignore` so credentials and personal data are not pushed to GitHub.

