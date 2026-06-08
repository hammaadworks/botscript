# /// script
# dependencies = [
#   "selenium",
#   "questionary",
#   "rich",
# ]
# ///

"""
WhatsApp Master Automator
=========================
A sophisticated Selenium-based tool for automating WhatsApp Web messaging.
Supports text, documents, and media with robust error handling and an interactive CLI.

Features:
- Search and select contacts/groups automatically.
- Send personalized text messages.
- Attach and send documents, images, and videos.
- Interactive CLI for ease of use.
- Secure session management (optional).

Author: Mohammed Hammaad Mateen
License: MIT
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import questionary
from rich.console import Console

console = Console()

class WhatsAppMaster:
    """
    Main controller for WhatsApp Web automation.
    """
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "https://web.whatsapp.com/"

    def launch(self):
        """Initializes the browser and waits for the QR scan."""
        console.print("[bold green]Launching WhatsApp Web...[/bold green]")
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.get(self.base_url)
        
        console.print("[bold yellow]Action Required: Please scan the QR code to log in.[/bold yellow]")
        # Wait until the search bar is visible to confirm login
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            console.print("[bold green]Login successful![/bold green]")
        except TimeoutException:
            console.print("[bold red]Timeout: Login took too long or was interrupted.[/bold red]")
            self.quit()
            sys.exit(1)

    def find_contact(self, name):
        """Searches for a contact or group and selects it."""
        try:
            # Locate the search box
            search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            search_box.click()
            search_box.clear()
            search_box.send_keys(name)
            time.sleep(1.5)
            search_box.send_keys(Keys.ENTER)
            console.print(f"[green]✓ Found and selected: {name}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error: Could not find contact '{name}': {e}[/red]")
            return False

    def send_text(self, message):
        """Sends a text message to the currently selected contact."""
        try:
            # Find the message input area
            msg_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]')))
            msg_box.send_keys(message)
            msg_box.send_keys(Keys.ENTER)
            console.print("[green]✓ Message sent![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error sending text: {e}[/red]")
            return False

    def send_attachment(self, file_path, file_type="document"):
        """Sends a file (document or media) to the currently selected contact."""
        if not os.path.exists(file_path):
            console.print(f"[red]Error: File not found at {file_path}[/red]")
            return False

        try:
            # Click the 'Attach' icon
            attach_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]')))
            attach_btn.click()
            time.sleep(1)

            # Map file types to input selectors
            if file_type == "media":
                # For Images & Videos
                accept_attr = "image/*,video/mp4,video/3gpp,video/quicktime"
            else:
                # For Documents
                accept_attr = "*"

            file_input = self.driver.find_element(By.XPATH, f'//input[@accept="{accept_attr}"]')
            file_input.send_keys(file_path)
            
            # Wait for the preview/send button to appear after upload
            send_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-testid="send"]')))
            send_btn.click()
            
            console.print(f"[green]✓ {file_type.capitalize()} sent successfully![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error sending attachment: {e}[/red]")
            return False

    def quit(self):
        if self.driver:
            console.print("[bold yellow]Closing session...[/bold yellow]")
            self.driver.quit()

def main():
    console.rule("[bold green]WhatsApp Master Automator[/bold green]")
    
    automator = WhatsAppMaster()
    try:
        automator.launch()
        
        while True:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Send Message",
                    "Send Attachment",
                    "Switch Contact",
                    "Exit"
                ]
            ).ask()
            
            if action == "Exit":
                break
                
            if action == "Switch Contact" or action == "Send Message" or action == "Send Attachment":
                contact = questionary.text("Enter contact or group name:").ask()
                if not automator.find_contact(contact):
                    continue
            
            if action == "Send Message":
                msg = questionary.text("Enter your message:").ask()
                automator.send_text(msg)
                
            elif action == "Send Attachment":
                f_type = questionary.select("File type:", choices=["document", "media"]).ask()
                f_path = questionary.text("Enter full file path:").ask()
                automator.send_attachment(f_path, f_type)
                
            console.print("\n[bold cyan]--- Action Complete ---[/bold cyan]\n")
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user.[/bold red]")
    finally:
        automator.quit()
        console.print("[bold green]Alhamdulillah: Exiting gracefully.[/bold green]")

if __name__ == "__main__":
    main()
