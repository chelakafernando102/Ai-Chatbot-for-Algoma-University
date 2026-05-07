import json
import os
import re
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

Answer clearly, briefly, and professionally.

Focus on:
- academics
- tuition
- student support
- programs
- registration
- scholarships
- residence
- student life
- university services

If unsure, suggest contacting:
- Registrar
- Academic Advising
- Student Success
- Official Algoma University website

Do not invent fake policies or fake university information.
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


def load_knowledge_base():
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {"questions": []}

        questions = data.get("questions", [])

        if not isinstance(questions, list):
            return {"questions": []}

        return data

    except FileNotFoundError:
        print(f"Knowledge base not found: {KNOWLEDGE_BASE_PATH}")
        return {"questions": []}

    except json.JSONDecodeError as error:
        print(f"Knowledge base JSON error: {error}")
        return {"questions": []}

    except Exception as error:
        print(f"Knowledge base loading error: {error}")
        return {"questions": []}


def normalize_text(text):
    text = str(text).strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_course_code(text):
    match = re.search(r"\b[A-Z]{4}\s?\d{4}\b", text.upper())
    return match.group(0).replace(" ", "") if match else None


def find_knowledge_base_answer(user_question):
    knowledge_base = load_knowledge_base()
    question_items = knowledge_base.get("questions", [])

    normalized_question = normalize_text(user_question)
    user_words = set(normalized_question.split())

    if not normalized_question:
        return None

    # 1. Exact match only
    for item in question_items:
        if not isinstance(item, dict):
            continue

        question = normalize_text(item.get("question", ""))

        if question == normalized_question:
            return item.get("answer")

    # 2. Short keyword match only for short user messages
    if len(user_words) <= 3:
        for item in question_items:
            if not isinstance(item, dict):
                continue

            question = normalize_text(item.get("question", ""))

            if question and question == normalized_question:
                return item.get("answer")

    # 3. Strong smart match
    best_answer = None
    best_score = 0

    for item in question_items:
        if not isinstance(item, dict):
            continue

        question = normalize_text(item.get("question", ""))
        question_words = set(question.split())

        if not question_words:
            continue

        score = len(user_words & question_words)
        required_score = max(2, len(question_words))

        if len(user_words) <= 4 and score >= required_score and score > best_score:
            best_score = score
            best_answer = item.get("answer")

    return best_answer


def format_answer(answer):
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


def can_register(course_code, student=DEMO_STUDENT):
    course_code = course_code.upper()

    if course_code not in COURSE_PREREQUISITES:
        return {
            "eligible": False,
            "message": f"I could not find prerequisite data for {course_code}.",
        }

    prerequisites = COURSE_PREREQUISITES[course_code]

    completed = set(student.get("completed", []))
    failed = set(student.get("failed", []))

    failed_prerequisites = [
        course for course in prerequisites if course in failed
    ]

    missing_prerequisites = [
        course for course in prerequisites
        if course not in completed and course not in failed
    ]

    if failed_prerequisites:
        return {
            "eligible": False,
            "message": (
                f"You cannot register for {course_code} because you failed "
                f"prerequisite(s): {', '.join(failed_prerequisites)}."
            ),
        }

    if missing_prerequisites:
        return {
            "eligible": False,
            "message": (
                f"You cannot register for {course_code} because you are missing "
                f"prerequisite(s): {', '.join(missing_prerequisites)}."
            ),
        }

    return {
        "eligible": True,
        "message": f"You are eligible to register for {course_code}.",
    }


def suggest_eligible_courses(student=DEMO_STUDENT, excluded_course=None):
    suggestions = []

    for course_code in COURSE_PREREQUISITES:
        if excluded_course and course_code == excluded_course:
            continue

        result = can_register(course_code, student)

        if result["eligible"]:
            suggestions.append(course_code)

    return suggestions


def is_registration_question(message):
    lowered = message.lower()

    keywords = [
        "register",
        "registration",
        "enroll",
        "enrol",
        "eligible",
        "prerequisite",
        "prereq",
        "take course",
        "can i take",
        "can i register",
    ]

    return any(keyword in lowered for keyword in keywords)


def ask_gemini(message):
    if not GEMINI_API_KEY:
        return "Gemini API key is missing. Please check your .env file."

    try:
        print("GEMINI CALLED")

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG,
            system_instruction=SYSTEM_INSTRUCTION,
        )

        response = model.generate_content(message)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "I could not generate a response. Please try rephrasing your question."

    except Exception as error:
        print(f"Gemini error: {error}")
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
        "knowledge_base_path": str(KNOWLEDGE_BASE_PATH),
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "response": "Please type a question first.",
            "source": "validation",
        }), 400

    course_code = extract_course_code(message)

    if is_registration_question(message) and course_code:
        result = can_register(course_code)
        response_text = result["message"]

        if not result["eligible"]:
            suggestions = suggest_eligible_courses(excluded_course=course_code)

            if suggestions:
                response_text += (
                    "\n\nEligible alternative courses: "
                    + ", ".join(suggestions)
                )

        return jsonify({
            "response": response_text,
            "source": "course_rules",
        })

    kb_answer = find_knowledge_base_answer(message)

    if kb_answer is not None:
        return jsonify({
            "response": format_answer(kb_answer),
            "source": "knowledge_base",
        })

    return jsonify({
        "response": ask_gemini(message),
        "source": "gemini",
    })


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "error": "Route not found.",
    }), 404


@app.errorhandler(500)
def server_error(_error):
    return jsonify({
        "error": "Internal server error.",
    }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
