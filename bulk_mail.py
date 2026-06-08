# /// script
# dependencies = [
#   "python-dotenv",
#   "rich",
# ]
# ///

import smtplib
import csv
import os
import io
import time
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme

# Custom theme for a professional look
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

console = Console(theme=custom_theme)

# Try to load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURATION ---
# Replace these with your actual credentials or set them as environment variables in .env
MY_EMAIL = os.getenv("MY_EMAIL", "your_email@gmail.com")
MY_PASSWORD = os.getenv("MY_PASSWORD", "your_app_password")

# Recipient data in CSV format (NAME,EMAIL)
CSV_DATA = """NAME,EMAIL
Mohammed Hammaad Mateen,myfriendhammad@gmail.com
Mr. Mahesh,mahes@bizedgedisha.com
Dr. Krita,krita@bizedgedisha.com
Mumineen,mumineen@bizedgedisha.com
Abdul Mateen,myfriendmateen@gmail.com
"""
# ---------------------

def send_bulk_emails():
    """Sends personalized emails with a beautiful CLI interface."""
    
    console.print(Panel.fit(
        "[bold highlight]Bulk Mailer Pro[/bold highlight]\n"
        "[white]High-Performance Personalized Email Automator[/white]",
        border_style="highlight"
    ))

    if MY_EMAIL == "your_email@gmail.com" or MY_PASSWORD == "your_app_password":
        console.print("[error][!] Configuration Error:[/error] Please update MY_EMAIL and MY_PASSWORD.")
        console.print("Set them in your [info].env[/info] file or edit the [info]CONFIGURATION[/info] section in the script.")
        return

    # Parse CSV data
    f = io.StringIO(CSV_DATA.strip())
    reader = csv.DictReader(f)
    recipients = list(reader)

    if not recipients:
        console.print("[error][!] No recipients found in CSV_DATA.[/error]")
        return

    # Show Preview Table
    table = Table(title="Recipient Preview", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="white")
    table.add_column("Email", style="info")
    
    for idx, r in enumerate(recipients, 1):
        table.add_row(str(idx), r['NAME'], r['EMAIL'])
    
    console.print(table)
    console.print(f"\n[info]Ready to send {len(recipients)} emails from:[/info] [highlight]{MY_EMAIL}[/highlight]\n")

    try:
        # Establish a connection to the SMTP server
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            login_task = progress.add_task("[yellow]Connecting to SMTP...", total=None)
            s = smtplib.SMTP(host='smtp.gmail.com', port=587)
            s.starttls()
            s.login(MY_EMAIL, MY_PASSWORD)
            progress.update(login_task, description="[success]Connected & Logged In[/success]", completed=True)

            send_task = progress.add_task("[cyan]Sending Emails...", total=len(recipients))
            
            count = 0
            for r in recipients:
                name = r['NAME']
                email = r['EMAIL']
                
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
                    progress.advance(send_task)
                    console.print(f"  [success]✓[/success] Sent to [white]{name}[/white] ([dim]{email}[/dim])")
                except Exception as e:
                    console.print(f"  [error]✗[/error] Failed for [white]{name}[/white]: [red]{e}[/red]")
                
                time.sleep(0.2) # Small delay for stability
                del msg

            s.quit()

        console.print(Panel(
            f"[bold success]Alhamdulillah! Process Completed.[/bold success]\n"
            f"Successfully sent [highlight]{count}[/highlight] out of [highlight]{len(recipients)}[/highlight] emails.",
            title="Summary",
            border_style="success"
        ))

    except smtplib.SMTPAuthenticationError:
        console.print("\n[error][!] SMTP Authentication Error (535).[/error]")
        console.print("Ensure you are using an [bold]App Password[/bold] instead of your regular password.")
        console.print("Create one here: [link=https://myaccount.google.com/apppasswords]https://myaccount.google.com/apppasswords[/link]")
    except Exception as e:
        console.print(f"\n[error][!] SMTP Error:[/error] {e}")

if __name__ == "__main__":
    send_bulk_emails()
