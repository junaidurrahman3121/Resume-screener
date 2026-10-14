# AI Resume Screener (Gemini)

Upload resumes (PDF, DOCX, TXT), paste a job description, and get every candidate scored 0-100 with matched/missing skills, strengths, concerns, and tailored interview questions. Results are ranked and exportable to CSV. Powered by Google Gemini.

## Setup (step by step)

### 1. Prerequisites
- Python 3.9 or newer (`python --version`)
- A Gemini API key from https://aistudio.google.com/apikey (free tier available)

### 2. Get the project
Put these files in one folder, e.g. `resume-screener/`:
`app.py`, `screener.py`, `requirements.txt`, `.env.example`

### 3. Create a virtual environment
```bash
cd resume-screener
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Add your API key
```bash
cp .env.example .env        # Windows: copy .env.example .env
```
Open `.env` and replace `your-gemini-api-key-here` with your real key:
```dotenv
GEMINI_API_KEY=AIza...
```

### 6. Run the app
```bash
streamlit run app.py
```
Your browser opens at http://localhost:8501.

### 7. Use it
1. Paste the job description (optionally add must-have requirements).
2. Upload one or more resumes.
3. Click **Screen resumes**.
4. Review the ranked table, expand each candidate for details, and download the CSV.

## How it works
- `extract_text()` reads PDF/DOCX/TXT into plain text.
- `screen_resume()` sends the job description + resume to Gemini with a JSON response schema (a Pydantic model), so output always has the same fields.
- `app.py` runs this for each file, sorts by score, and displays the results.

## Tuning
- **Model:** change in the sidebar or set `GEMINI_MODEL` in `.env`. `gemini-2.5-flash` is fast and cheap; `gemini-2.5-pro` is more thorough. Newer Gemini models work too if your key has access.
- **Scoring behavior:** edit `SYSTEM_PROMPT` in `screener.py`.
- **Shortlist cutoff:** the sidebar slider.

## Troubleshooting
| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Check `.env` exists in the folder you run from, with no quotes or spaces around the key |
| "Resume text is empty or too short" | The PDF is likely a scanned image; run OCR first (e.g. `ocrmypdf in.pdf out.pdf`) |
| `ModuleNotFoundError` | Activate the virtual environment, then rerun `pip install -r requirements.txt` |
| 400 / API key not valid | Key is wrong or the Generative Language API is not enabled for it; create a new key in AI Studio |
| 404 model not found | The model name is wrong or unavailable to your key; pick another in the sidebar |
| 429 rate limit | Free tier limits are low; screen fewer resumes at once, wait a minute, or enable billing |
| "no result (blocked)" | Gemini's safety filter blocked the response; retry or check the resume content |

## Responsible use
This tool supports recruiters; it must not make hiring decisions alone. Resume screening can be regulated (e.g. NYC Local Law 144, EU AI Act "high-risk" category, GDPR for personal data). Disclose AI use to candidates where required, audit results for bias regularly, and delete resume data you no longer need. Resumes are sent to the Google Gemini API for processing; note that free-tier usage may be used by Google to improve its products, so use a paid/billed key for real candidate data.

## Next steps (optional)
- Add OCR for scanned resumes (`pytesseract`).
- Store results in a database (SQLite/Postgres) for history.
- Deploy to Streamlit Community Cloud, adding the key under Secrets instead of `.env`.
