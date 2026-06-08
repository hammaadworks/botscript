# /// script
# dependencies = [
#   "python-dotenv",
# ]
# ///

import smtplib
import csv
import os
import io
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Try to load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURATION ---
# Replace these with your actual credentials or set them as environment variables in .env
MY_EMAIL = "myfriendhammad@gmail.com"
MY_PASSWORD = "Hammaad@g00gle"
MY_PASSWORD = "ovqk ontt riek ccyr"

# Recipient data in CSV format (NAME,EMAIL)
CSV_DATA = """NAME,EMAIL
Py bhai, hammaad.py@gmail.com
Swe bhai, hammaad.swe@gmail.com
"""
# ---------------------

def send_bulk_emails():
    """Sends personalized emails to recipients listed in the CSV_DATA constant."""
    if not MY_EMAIL or not MY_PASSWORD:
        print("Error: Please update MY_EMAIL and MY_PASSWORD in the script configuration section.")
        return

    try:
        # Establish a connection to the SMTP server
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as s:
            s.starttls()
            s.login(MY_EMAIL, MY_PASSWORD)

            count = 0
            # Read data from the CSV_DATA constant
            f = io.StringIO(CSV_DATA.strip())
            dataset = csv.reader(f, delimiter=',')
            try:
                next(dataset)  # Skip the header row
            except StopIteration:
                print("Error: CSV data is empty.")
                return

            for row in dataset:
                if not row or len(row) < 2:
                    continue
                
                name = row[0]
                email = row[1]
                
                msg = MIMEMultipart()
                content_template = Template(
                    "Dear ${NAME},\n\n"
                    "This is a custom bulk email generator script built by "
                    "Mohammed Hammaad Mateen.\n\n"
                    "Thank You"
                )
                subject_template = Template("Custom bulk email for ${NAME}")
                
                content = content_template.substitute(NAME=name)
                subject = subject_template.substitute(NAME=name)
                
                msg['From'] = MY_EMAIL
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(content, 'plain'))
                
                try:
                    s.send_message(msg)
                    count += 1
                    print(f"{count}. Sent to {name} --> {email}")
                except Exception as e:
                    print(f"Failed to send to {name} ({email}): {e}")
                
                del msg

            print(f"\nSuccessfully sent mails to {count} recipients.")
            print("Alhamdulillah")

    except smtplib.SMTPAuthenticationError:
        print("\n[!] SMTP Authentication Error (535).")
        print("    If you are using Gmail, ensure you are using an 'App Password' instead of your regular password.")
        print("    You can create one at: https://myaccount.google.com/apppasswords")
    except Exception as e:
        print(f"SMTP Error: {e}")

if __name__ == "__main__":
    send_bulk_emails()
