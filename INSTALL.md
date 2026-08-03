# WebSentinel - Installation Guide

## Quick Setup (Windows)

1. **Run the setup script:**
   ```
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all Python dependencies
   - Install Playwright Chromium browser

2. **Create your `.env` file:**
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Launch the application:**
   ```
   python launch.py
   ```

---

## Manual Installation

### Step 1: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```powershell
.\.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browser (IMPORTANT!)
```bash
python -m playwright install chromium
```

This step is **REQUIRED** for the visual browser testing feature!

### Step 5: Create Environment File
Create a file named `.env` in the project root:
```
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Starting the Interfaces

### Gradio Web Interface (Port 7860)
```bash
python interfaces/web_interface.py
```
Then open: http://127.0.0.1:7860

### Streamlit Interface (Port 8501)
```bash
streamlit run interfaces/streamlit_interface.py
```
Then open: http://localhost:8501

### Using the Launcher
```bash
python launch.py
```

---

## Dependencies Summary

| Package | Purpose |
|---------|---------|
| `playwright` | Visual browser automation |
| `gradio` | Gradio web interface |
| `streamlit` | Streamlit web interface |
| `langchain-google-genai` | Google Gemini AI integration |
| `reportlab` | PDF report generation |
| `httpx` | HTTP requests |
| `pydantic` | Data validation |

---

## Troubleshooting

### "Playwright browser not found"
Run: `python -m playwright install chromium`

### "GOOGLE_API_KEY not found"
Create a `.env` file with your API key.

### "Module not found"
Ensure virtual environment is activated and dependencies installed.

---

## Project Structure

```
WebSentinel/
├── interfaces/
│   ├── web_interface.py     # Gradio interface
│   └── streamlit_interface.py # Streamlit interface
├── core/
│   ├── ai_analyzer.py
│   ├── security_scanner.py
│   ├── accessibility_analyzer.py
│   └── performance_predictor.py
├── tests/
├── reports/               # Generated PDF/JSON reports
├── agent_screenshots/     # Screenshots from tests
├── configs/config.yaml    # Configuration
├── .env                   # API keys (create this!)
├── requirements.txt       # Python dependencies
├── setup.bat             # Windows setup script
└── launch.py             # Main launcher
```
