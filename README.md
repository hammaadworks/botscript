# Python Bots & Scripts Collection

A collection of useful Python scripts for automation, utility, and fun. This repository is being systematically reviewed and refined to ensure high reliability, modern standards, and clear documentation.

## 🚀 Script Catalog

### 📺 Media Utilities
*   **[Utube.py](./Utube.py)**: A robust YouTube playlist/video downloader powered by `yt-dlp`. Features resolution selection and error handling.

### 🤖 Automation Bots
*   **[whatsapp_master.py](./whatsapp_master.py)**: Sophisticated WhatsApp automation with an interactive CLI. Supports text, images, and documents.
*   **[automate_google_forms.py](./automate_google_forms.py)**: A universal Google Forms automator. Replaces all previous form-specific bots.
*   **[Auto GMerchantFeed.py](./Auto%20GMerchantFeed.py)**: Automates navigation to Google Merchant Center feeds. (Requires `.env` setup).
*   **[Auto OpIMFeed.py](./Auto%20OpIMFeed.py)**: Automates product feed management on WordPress/Infinique backends.

### 🛠️ Utilities
*   **[bulk_mail.py](./bulk_mail.py)**: Secure bulk email sender using Gmail SMTP and environment variables. Features personalized templates and CSV support.
*   **[documentor_bot.py](./documentor_bot.py)**: AI-powered script that uses Google Gemini to generate high-quality docstrings and format Python code using `black` and `isort`.
*   **[workout.py](./workout.py)**: Generates a personalized workout plan PDF using `fpdf2`.

### 🎮 Games & Fun
*   **[Ztype_Game_Bot.py](./Ztype_Game_Bot.py)**: An automated bot for the Ztype typing game using EasyOCR for text recognition and PyAutoGUI for typing.

---

## ⚙️ Setup & Usage

### Prerequisites
- Python 3.10+
- Chrome Browser (for Selenium-based bots)
- [FFmpeg](https://ffmpeg.org/) (recommended for `Utube.py` high-res downloads)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your credentials in a `.env` file (see `.env.example`):
   ```bash
   cp .env.example .env
   # Edit .env with your secrets
   ```

---

## 📂 Advanced Projects
*   **[mytube/](./mytube/)**: A more advanced, full-stack YouTube management project featuring a CLI and a Web UI.

---
*Maintained with ❤️ by Mohammed Hammaad Mateen*
