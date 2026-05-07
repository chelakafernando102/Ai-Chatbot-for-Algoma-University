import json
import os
import re
from difflib import get_close_matches
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import google.generativeai as genai

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.json"

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1200,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

SYSTEM_INSTRUCTION = """
You are AlgomaU Virtual Assistant, a friendly academic chatbot for Algoma University students.
Answer clearly, briefly, and professionally. Focus on academic help, course registration,
student services, fees, programs, and general student-life questions. If you are unsure,
say so and suggest contacting the Registrar, Student Success, or the official Algoma website.
Do not invent official policy details.
""".strip()

COURSE_PREREQUISITES = {
    "COSC2006": ["COSC1047", "MATH1056"],
    "COSC2007": ["COSC2006"],
    "COSC2307": ["COSC1046"],
    "COSC2396": ["COSC2006"],
    "COSC2406": ["COSC1047", "MATH1056"],
    "COSC2956": ["COSC1046"],
    "COSC3106": ["COSC2006", "MATH2056"],
    "COSC3117": ["COSC2007"],
    "COSC3127": ["COSC2006", "COSC2406"],
    "COSC3406": ["COSC2006", "COSC2406"],
    "COSC3407": ["COSC2006", "COSC2406"],
    "COSC3506": [],
    "COSC3707": ["COSC2006"],
    "COSC3796": ["COSC2006"],
    "COSC4106": ["COSC2007", "COSC3106"],
    "COSC4426": [],
    "COSC4436": ["COSC3406", "COSC3407"],
    "COSC4806": ["COSC2307", "COSC2956"],
}

DEMO_STUDENT = {
    "completed": ["COSC1046", "COSC2006"],
    "failed": ["COSC1047"],
}

app = Flask(__name__)


def load_knowledge_base() -> dict:
    try:
        with KNOWLEDGE_BASE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict) or "questions" not in data:
            return {"questions": []}
        return data
    except FileNotFoundError:
        return {"questions": []}
    except json.JSONDecodeError:
        return {"questions": []}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def extract_course_code(text: str) -> str | None:
    match = re.search(r"\b[A-Z]{4}\s?\d{4}\b", text.upper())
    return match.group(0).replace(" ", "") if match else None


def find_knowledge_base_answer(user_question: str) -> str | list | None:
knowledge_base = load_knowledge_base()
question_items = knowledge_base.get("questions", [])


normalized_question = normalize_text(user_question)


for item in question_items:
    if not isinstance(item, dict):
        continue

    question = normalize_text(item.get("question", ""))

    if question == normalized_question:
        return item.get("answer")


for item in question_items:
    if not isinstance(item, dict):
        continue

    question = normalize_text(item.get("question", ""))

    if question and question in normalized_question:
        return item.get("answer")

user_words = set(normalized_question.split())

best_answer = None
best_score = 0

for item in question_items:
    if not isinstance(item, dict):
        continue

    question = normalize_text(item.get("question", ""))
    question_words = set(question.split())

    score = len(user_words & question_words)

    if score > best_score:
        best_score = score
        best_answer = item.get("answer")
        
    if best_score >= 1:
    return best_answer

return None


    question_map = {
        normalize_text(item.get("question", "")): item.get("answer")
        for item in question_items
        if isinstance(item, dict) and item.get("question")
    }

    normalized_question = normalize_text(user_question)
    if normalized_question in question_map:
        return question_map[normalized_question]

    possible_questions = list(question_map.keys())
    matches = get_close_matches(normalized_question, possible_questions, n=1, cutoff=0.58)
    if matches:
        return question_map[matches[0]]

    return None


def format_answer(answer: str | list | dict) -> str:
    if isinstance(answer, str):
        return answer
    if isinstance(answer, list):
        lines = []
        for item in answer:
            if isinstance(item, dict):
                course = item.get("course_name", "Course")
                location = item.get("location", "Location not listed")
                lines.append(f"• {course} — {location}")
            else:
                lines.append(f"• {item}")
        return "\n".join(lines)
    if isinstance(answer, dict):
        return json.dumps(answer, indent=2)
    return str(answer)


def can_register(course_code: str, student: dict = DEMO_STUDENT) -> dict:
    course_code = course_code.upper()

    if course_code not in COURSE_PREREQUISITES:
        return {
            "eligible": False,
            "message": f"I could not find prerequisite data for {course_code}. Please confirm this course code with the official Algoma course calendar or an academic advisor.",
        }

    prerequisites = COURSE_PREREQUISITES[course_code]
    completed = set(student.get("completed", []))
    failed = set(student.get("failed", []))

    failed_prerequisites = [course for course in prerequisites if course in failed]
    missing_prerequisites = [course for course in prerequisites if course not in completed]

    if failed_prerequisites:
        return {
            "eligible": False,
            "message": f"You cannot register for {course_code} because you previously failed prerequisite(s): {', '.join(failed_prerequisites)}.",
        }

    if missing_prerequisites:
        return {
            "eligible": False,
            "message": f"You cannot register for {course_code} because you have not completed prerequisite(s): {', '.join(missing_prerequisites)}.",
        }

    return {
        "eligible": True,
        "message": f"You are eligible to register for {course_code} based on this demo student record.",
    }


def suggest_eligible_courses(student: dict = DEMO_STUDENT, excluded_course: str | None = None) -> list[str]:
    suggestions = []
    for course_code in COURSE_PREREQUISITES:
        if excluded_course and course_code == excluded_course:
            continue
        result = can_register(course_code, student)
        if result["eligible"]:
            suggestions.append(course_code)
    return suggestions


def is_registration_question(message: str) -> bool:
    lowered = message.lower()
    keywords = ["register", "registration", "enroll", "enrol", "take", "eligible", "prerequisite", "prereq"]
    return any(keyword in lowered for keyword in keywords) or bool(extract_course_code(message))


def ask_gemini(message: str) -> str:
    if not GEMINI_API_KEY:
        return (
            "Gemini is not connected yet. Add your API key to a .env file as GEMINI_API_KEY, "
            "restart Flask, and try again."
        )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG,
            system_instruction=SYSTEM_INSTRUCTION,
        )
        response = model.generate_content(message)
        return (response.text or "I could not generate a response. Please try again.").strip()
    except Exception as error:
        return f"Gemini error: {error}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY),
        "knowledge_base_loaded": KNOWLEDGE_BASE_PATH.exists(),
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"response": "Please type a question first."}), 400

    course_code = extract_course_code(message)

    if is_registration_question(message) and course_code:
        result = can_register(course_code)
        response_text = result["message"]
        if not result["eligible"]:
            suggestions = suggest_eligible_courses(excluded_course=course_code)
            if suggestions:
                response_text += "\n\nEligible alternatives based on the demo record: " + ", ".join(suggestions)
        return jsonify({"response": response_text, "source": "course_rules"})

    kb_answer = find_knowledge_base_answer(message)
    if kb_answer is not None:
        return jsonify({"response": format_answer(kb_answer), "source": "knowledge_base"})

    return jsonify({"response": ask_gemini(message), "source": "gemini"})


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Route not found."}), 404


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
