# 🤖 Python Bots: The Ultimate Automation Suite

A collection of high-performance, beautiful, and autonomous Python scripts for everyday automation. Every script is a self-contained "one-filer" powered by `uv` for instant execution.

---

## 🚀 Featured Scripts

### 1. 📧 Bulk Mailer Pro
A sophisticated, personalized email automator with a professional CLI.
- **File:** `bulk_mail.py`
- **Features:** 
  - Rich CLI with progress bars and status updates.
  - CSV data embedded directly in the script.
  - Secure credential management via `.env` or constants.
- **Run:** `uv run bulk_mail.py`
- **Visuals:**
  ![Bulk Mailer Demo](assets/bulk_mail_demo.png)
  
  > **Demo Video:**
  > https://github.com/MohammedHMateen/python-bots/raw/main/assets/bulk_malier.mp4

### 2. 📝 Google Forms Master
An autonomous live-filling mode automator. No hardcoded IDs—it uses heuristics to fill any form.
- **File:** `automate_google_forms.py`
- **Features:** 
  - Real-time DOM scanning.
  - Intelligent field type detection.
  - Interactive CLI for custom overrides.
- **Run:** `uv run automate_google_forms.py`
- **Visuals:**
  ![Google Forms Demo](assets/forms_demo.png)

### 3. 💬 WhatsApp Master
A Selenium-based powerhouse for WhatsApp Web automation.
- **File:** `automate_whatsapp.py`
- **Features:** 
  - Contact/Group search.
  - Media and document attachment support.
  - Interactive selection.
- **Run:** `uv run automate_whatsapp.py`
- **Visuals:**
  ![WhatsApp Master Demo](assets/whatsapp_demo.png)

### 4. 📄 Documentor Bot
Your AI-powered assistant for documenting codebases.
- **File:** `automate_code_documentation.py`
- **Features:** 
  - Powered by Gemini 2.0 Flash.
  - Auto-formats and documents Python files.
- **Run:** `uv run automate_code_documentation.py`

---

## 🛠️ How to Add Assets (Images/Videos)

To show off your scripts beautifully:
1. Create an `assets/` folder in the root directory.
2. Place your screenshots (`.png`, `.jpg`) or demos there.
3. Reference them in this README using `![Alt Text](assets/filename.png)`.
4. **Pro Tip:** For videos, GitHub supports embedding MP4s or GIFs directly in the README!

---

## ⚙️ Global Setup

1. **Install `uv`:** The fastest way to run these scripts.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Configure Credentials:** Create a `.env` file in the root:
   ```env
   MY_EMAIL=your_email@gmail.com
   MY_PASSWORD=your_app_password
   GEMINI_API_KEY=your_key
   ```

---

*Built with ❤️ by Mohammed Hammaad Mateen. Alhamdulillah.*
