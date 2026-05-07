# AlgomaU Virtual Assistant 🎓

An AI-powered university support assistant developed for :contentReference[oaicite:0]{index=0} students as part of a Topics in Computer Science II group project under Professor :contentReference[oaicite:1]{index=1}.

This project was collaboratively developed by Chelaka Fernando, Sonal Liyanage, and Marizza Ranasinghe using Python, Flask, JavaScript, and Google Gemini AI. The application provides intelligent academic assistance, course registration guidance, prerequisite validation, and real-time conversational support through a responsive web interface.

---

# 🌐 Live Demo

🚀 https://ai-chatbot-for-algoma-university.onrender.com

---

# ✨ Features

## 🤖 AI-Powered Chatbot
- Integrated with Google Gemini AI for intelligent conversational support
- Provides real-time responses to student inquiries
- Handles academic and campus-related questions naturally

## 📚 Hybrid Search-First Architecture
- Uses a local JSON knowledge base for fast responses
- Implements fuzzy matching for accurate FAQ retrieval
- Falls back to Gemini AI when information is unavailable locally

## 🎯 Course Registration & Eligibility Checker
- Automatically detects course codes from user input
- Validates prerequisite completion
- Identifies failed or missing requirements
- Suggests alternative eligible courses

## 💻 Modern Responsive Interface
- Clean and responsive user interface
- Optimized for desktop and mobile devices
- Real-time chat experience using JavaScript and Flask APIs

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic |
| Flask | Web framework & REST API |
| JavaScript | Frontend interactivity |
| HTML5 | Web structure |
| CSS3 | Styling & responsive design |
| Google Gemini API | AI-generated responses |
| JSON | Knowledge base storage |
| dotenv | Environment variable management |

---

# 📚 Functionalities

## 🎓 Academic Assistance

Students can receive support and information related to:

- Programs & majors
- Tuition fees
- Scholarships
- Campus information
- Academic advising
- Residence options
- Student services
- Course registration

---

## 🧠 Intelligent AI Support

The chatbot follows a hybrid response system:

1. Searches the local university knowledge base
2. Uses fuzzy matching to find the best response
3. Falls back to Google Gemini AI when needed

This approach improves both response speed and conversational flexibility.

---

## 📖 Course Eligibility Checker

The registration support module can:

- Detect course codes automatically
- Validate prerequisites
- Check failed or missing requirements
- Suggest alternative course pathways

---

# 📂 Project Structure

```bash
algomau-chatbot/
│
├── app.py
├── knowledge_base.json
├── requirements.txt
├── .env
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/algomau-chatbot.git
cd algomau-chatbot
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure Environment Variables

Create a `.env` file in the project root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## 4️⃣ Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```bash
http://127.0.0.1:5000
```

---

# 🚀 Future Improvements

Planned enhancements include:

- Student authentication system
- Database integration
- Real-time university API connectivity
- Admin dashboard & analytics
- Voice assistant support
- Multi-language support
- Persistent chat history
- Course schedule integration

---

# 📸 Preview

A modern AI-powered university chatbot designed to provide students with accessible, real-time academic assistance and registration support.

---

# 👨‍💻 Contributors

## Chelaka Fernando
- LinkedIn: https://www.linkedin.com/in/chelaka-fernando-87529a213/
- GitHub: https://github.com/chelakafernando102

## Sonal Liyanage

## Marizza Ranasinghe

---

# 📄 License

This project was created for educational and portfolio purposes under the guidance of Prof. Sathaporn "Hubert" Hu, PhD 

This application is not officially affiliated with or endorsed by Algoma University
