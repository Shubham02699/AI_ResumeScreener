# 🤖 AI Resume Screener

A Python-based desktop application that uses AI to screen, analyse, and rank resumes more intelligently than traditional ATS systems.

Built with **Streamlit**, **TF-IDF (scikit-learn)**, and **Google Gemini API**.

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-screener.git
cd ai-resume-screener
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your Gemini API key
```bash
cp .env.example .env
# Open .env and replace 'your_gemini_api_key_here' with your actual key
# Get a free key at: https://aistudio.google.com/app/apikey
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 Resume Parsing | Supports PDF and DOCX files |
| ⚙️ ATS Mode | TF-IDF + cosine similarity (fully offline) |
| 🤖 AI Mode | Google Gemini — reads context, not just keywords |
| 🔀 Hybrid Mode | Weighted combination of ATS + AI (recommended) |
| 📊 Ranked Results | Top-3 podium + full table with scores & reasoning |
| 💾 Export | Download results as CSV or Excel |

---

## 📁 Project Structure

```
ai-resume-screener/
├── app.py              # Main Streamlit app
├── ats_scorer.py       # TF-IDF cosine similarity scoring
├── ai_scorer.py        # Google Gemini API scoring
├── resume_parser.py    # PDF & DOCX text extraction
├── hybrid_scorer.py    # Weighted score combination
├── utils.py            # Helpers: export, formatting, validation
├── requirements.txt
├── .env.example        # Copy to .env and add your API key
└── .gitignore
```

---

## 🔐 Security

- Your Gemini API key is stored in `.env` — never in source code
- `.env` is listed in `.gitignore` so it is never uploaded to GitHub

---

## ⚠️ Limitations

- Maximum 50 resumes per session (Gemini free tier rate limits)
- Scanned/image-based PDFs cannot be parsed (text-based PDFs only)
- Gemini free tier: ~15 requests/minute. A 4-second delay is applied between AI calls automatically

---

## 🔮 Future Enhancements (v2.0)

- Side-by-side candidate comparison view
- Resume feedback mode (tell candidates what to improve)
- Multi-job-description support
- Deploy to Streamlit Cloud (free hosting)
- Score distribution charts (matplotlib/seaborn)
- Support for OpenAI GPT-4 / other LLMs

---

## 🛠️ Tech Stack

- **Streamlit** — UI framework
- **pdfplumber** — PDF text extraction
- **python-docx** — DOCX text extraction
- **scikit-learn** — TF-IDF vectorization & cosine similarity
- **Google Generative AI SDK** — Gemini API integration
- **pandas + openpyxl** — Data handling & Excel export
- **python-dotenv** — Secure API key management

---

*Built as a learning project for AI/ML skill development — February 2026*
