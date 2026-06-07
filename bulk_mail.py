import smtplib
import csv
import os
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Securely retrieve credentials
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")

if not MY_EMAIL or not MY_PASSWORD:
    print("Error: Please set MY_EMAIL and MY_PASSWORD in a .env file.")
    exit(1)

def send_bulk_emails(csv_file_path):
    """Sends personalized emails to recipients listed in a CSV file.

    Args:
        csv_file_path (str): The path to the CSV file containing recipient data.
    """
    try:
        # Establish a connection to the SMTP server
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as s:
            s.starttls()
            s.login(MY_EMAIL, MY_PASSWORD)

            count = 0
            # Read data from the CSV file
            with open(csv_file_path, "r", encoding='utf-8') as file:
                dataset = csv.reader(file, delimiter=',')
                try:
                    next(dataset)  # Skip the header row
                except StopIteration:
                    print("Error: CSV file is empty.")
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
                        "Mohammed Hammaad Mateen for BizEdge Disha.\n\n"
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

    except Exception as e:
        print(f"SMTP Error: {e}")

if __name__ == "__main__":
    CSV_FILE = "bulk_mail.csv"
    if os.path.exists(CSV_FILE):
        send_bulk_emails(CSV_FILE)
    else:
        print(f"Error: {CSV_FILE} not found.")
