# KaagazAI

**An all-in-one PDF, document processing, and AI-powered report generation platform.**

KaagazAI combines the functionality of tools like iLovePDF with unique AI-powered features — a smart report generator, a multi-tool PDF workflow pipeline, media-to-text conversion, and a text-to-diagram concept visualizer — all in a single application.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [AI Providers](#ai-providers)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

KaagazAI is a document intelligence platform built around five core modules:

1. **PDF Processing** – Convert, organize, optimize, secure, and edit PDF files.
2. **Workflow Builder** – Chain multiple PDF tools together and run them sequentially on a single file, in a user-defined order.
3. **Report Generator** – Provide a topic and a custom list of headings; AI generates content for each section, which is assembled into a fully formatted PDF/Word report.
4. **Media & Text Converter** – Convert between text, images, PDFs, audio, and video (e.g., audio-to-text, video-to-text).
5. **Concept Visualizer** – Extract key concepts from dense text and render them as mind-maps/diagrams to aid understanding and retention.

---

## Features

### PDF Processing Module
- **Convert:** Word ↔ PDF, Excel ↔ PDF, PowerPoint ↔ PDF, Image ↔ PDF
- **Organize:** Merge, Split, Insert Page (at a specific position), Delete Pages, Remove Blank Pages, Extract Pages, Rotate, Reorder
- **Optimize:** Compress PDF, Repair PDF
- **Security:** Protect (password), Unlock, Watermark, Add Page Numbers
- **Edit:** Edit PDF, Sign PDF, Crop PDF
- **Advanced (planned):** PDF Compare, PDF to Excel, OCR for scanned PDFs, Redact PDF

### Workflow Builder (Multi-Tool Pipeline)
- Select multiple PDF tools at once (e.g., Insert Page, Delete Page, Compress)
- Assign an execution order/number to each selected tool
- Backend runs each tool sequentially, passing the output of one step as the input to the next
- Produces a single final PDF with all selected operations applied

### Report Generator
- User provides a topic and a fully customizable list of headings (no fixed template required)
- AI generates content for each heading based on the topic
- Auto-generated Table of Contents based on the heading list
- Formatting controls: font, size, spacing, alignment, page size/orientation, margins, color themes, cover page styles, section numbering
- Page-count control: content length is balanced across sections to match the requested number of pages
- Output as PDF or Word

### Media & Text Converter
- Text → Image
- PDF → Image, Word → Image
- Audio → Text (speech-to-text)
- Video → Text (audio extraction + speech-to-text)

### Concept Visualizer
- Extracts structure from text (rule-based or AI-based)
- Renders the structure as a mind-map/diagram using Mermaid.js
- Helps convert dense paragraphs into an easy-to-remember visual format

### Supporting Systems
- Temporary file storage with automatic deletion for privacy
- (Planned) User accounts, file history, saved templates
- Configurable AI provider (swap between Gemini, Grok, Claude via config)
- Rate limiting and file size limits

---

## Tech Stack

### Frontend
- HTML, CSS, JavaScript
- React.js
- Tailwind CSS
- Mermaid.js (diagram rendering)

### Backend
- Python
- FastAPI (or Flask)
- `pypdf`, `PyMuPDF` (PDF manipulation)
- Ghostscript (PDF compression)
- LibreOffice headless (Office file conversion)
- `pdf2docx` (PDF to Word)
- Tesseract OCR (scanned PDF text extraction)
- `python-docx` (Word report generation)
- WeasyPrint / `reportlab` (PDF report generation)
- OpenAI Whisper (speech-to-text)
- FFmpeg (video audio extraction)
- Pillow (image handling)

### Database
- PostgreSQL / MySQL (structured data: users, file history)
- MongoDB (optional, for flexible data like saved templates)

### Deployment
- Frontend: Vercel / Netlify
- Backend: Render / Railway (early stage) → AWS / DigitalOcean (at scale)
- File Storage: Local temp folder (early stage) → Cloudinary / AWS S3 (at scale)

---

## Project Structure

```
kaagazai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   ├── pdf_tools.py
│   │   │   ├── workflow.py
│   │   │   ├── report_generator.py
│   │   │   ├── media_converter.py
│   │   │   ├── visualizer.py
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── pdf_service/
│   │   │   ├── convert_service/
│   │   │   ├── workflow_service/
│   │   │   ├── report_service/
│   │   │   ├── media_service/
│   │   │   └── visualizer_service/
│   │   ├── models/
│   │   ├── utils/
│   │   └── temp_files/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
├── database/
├── docs/
├── .gitignore
└── README.md
```

---

## AI Providers

KaagazAI is designed to be AI-provider agnostic. The primary provider is configured via environment variables so it can be swapped without changing core logic.

| Provider | Model | Notes |
|---|---|---|
| **Google Gemini** (default) | Flash-Lite | Free tier, no credit card required, sufficient for report generation and structure extraction |
| xAI Grok | Grok Fast | Free sign-up credits, conditional larger free tier |
| Anthropic Claude | Haiku | Paid, higher accuracy for production use |

**Default provider:** Gemini Flash-Lite (free tier, ~1,000 requests/day, no billing required to start).

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js (LTS)
- Git
- LibreOffice (for Office file conversions)
- Ghostscript (for PDF compression)
- FFmpeg (for video/audio processing)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create a `.env` file in `backend/` with:
```
GEMINI_API_KEY=your_gemini_api_key_here
AI_PROVIDER=gemini
MAX_FILE_SIZE_MB=25
FILE_RETENTION_MINUTES=60
```

---

## Roadmap

| Phase | Focus |
|---|---|
| 0 | Environment setup, project scaffolding |
| 1 | Core PDF tools (Merge, Split, Insert/Delete Page, Rotate, Remove Blank Pages) |
| 2 | Optimize & security tools (Compress, Protect, Watermark) |
| 3 | Conversion tools (Word/Excel/PPT/Image ↔ PDF, OCR) |
| 4 | Workflow Builder (multi-tool pipeline) |
| 5 | Report Generator (AI content + formatting) |
| 6 | Media & Text Converter (audio/video to text) |
| 7 | Concept Visualizer (text to diagram) |
| 8 | User accounts, file history, safety systems |
| 9 | UI polish, testing, deployment |

See `docs/` for the full detailed roadmap and concept breakdown.

---

## Contributing

This is currently a solo/learning project. Suggestions and contributions are welcome once the core modules are functional — guidelines will be added as the project matures.

---

## License

License to be decided. Add a `LICENSE` file (e.g., MIT) before making the repository public if you intend to open-source it.