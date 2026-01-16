# 🤖 TalentScout – AI Hiring Assistant

TalentScout is an intelligent hiring assistant chatbot built to automate the **initial screening of candidates** for technical roles.  
It gathers candidate details, conducts a **context-aware technical interview**, records **time-based behavioral signals**, and notifies candidates via **automated email** upon completion.

---

## 🚀 Features

### ✅ Candidate Information Collection
- Full Name  
- Email Address (validated)  
- Phone Number (validated)  
- Current Location  
- Years of Experience  
- Desired Role  
- Tech Stack  

### 🧠 Technical Interview (LLM-powered)
- Dynamically generates **3–5 technical questions** based on the candidate’s tech stack  
- Questions are asked **one-by-one** for a natural interview flow  
- Maintains conversation context throughout the interview  

### ⏱️ Time-Based Behavioral Signal
- Tracks **time taken per technical question**
- Stores:
  - Individual response times
  - Total technical interview time
- Avoids unfair auto-scoring while still providing **useful recruiter insights**

### 📝 Candidate Feedback
- Self-reported confidence score (1–5)
- Optional feedback on interview experience

### 📧 Automated Email Notification
- Sends a **“Interview Completed”** email to the candidate
- Implemented using **Make (Integromat)** webhook + Gmail
- Scenario runs in **Always-On (Instant)** mode

### 🔐 Data Privacy
- Uses simulated/local data storage
- No hardcoded API keys
- No automated decision-making on candidate outcomes
- GDPR-aware design

---

## 🛠️ Tech Stack
- Python  
- Streamlit  
- Large Language Models (LLM)  
- Make (Integromat)  
- JSON  

---

## 📁 Project Structure

TalentScout/
├── app.py  
├── llm.py  
├── time_utils.py  
├── styles.py  
├── data/
│   └── candidates.json  
├── README.md  
└── .gitignore  

---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/your-username/TalentScout.git
cd TalentScout
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔁 Email Automation (Make)
- Custom Webhook triggers after interview completion
- Gmail module sends confirmation email
- Scenario runs in **Immediately as data arrives** mode

---

## 🧠 Prompt Design
- Prompts are crafted to:
  - Generate relevant technical questions
  - Match the declared tech stack
  - Maintain clarity and consistency

---

## 🧪 Data Handling
- Stored locally in `candidates.json`
- Includes:
  - Candidate profile
  - Technical Q&A
  - Time-based metrics
  - Confidence score & feedback

---

## 🎥 Demo
A short demo showcases:
- Full interview flow
- Technical question generation
- Timing logic
- Automated email trigger

---

## 🏁 Conclusion
TalentScout demonstrates practical use of LLMs with:
- Ethical evaluation
- Modular design
- Real-world automation
- Clean user experience

💡 Tip: You can type `exit` anytime during the interview to end the session.
