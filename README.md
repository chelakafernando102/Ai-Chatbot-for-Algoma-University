# AlgomaU Virtual Assistant

A Flask chatbot for Algoma University student questions. It uses:

- Local knowledge base answers
- Course prerequisite logic
- Gemini fallback responses
- Clean HTML/CSS/JavaScript frontend

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```bash
cp .env.example .env
```

Then paste your Gemini key into `.env`:

```env
GEMINI_API_KEY=your_key_here
```

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Test questions

- Hi
- What majors does Algoma University offer?
- What are the available courses for 3rd-year Computer Science students?
- Can I register for COSC3407?
- What are tuition fees?

## Important

Do not commit your `.env` file or API key to GitHub.
