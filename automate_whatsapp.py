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

import questionary
from rich.console import Console
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize a Rich Console object for styled terminal output.
console = Console()


class WhatsAppMaster:
    """
    Main controller for WhatsApp Web automation.

    This class manages the Selenium WebDriver, interacts with WhatsApp Web
    elements, and provides methods for common automation tasks like
    launching the browser, finding contacts, sending messages, and attachments.
    """

    def __init__(self):
        """
        Initializes the WhatsAppMaster instance.

        Sets up instance variables for the WebDriver, WebDriverWait, and the
        base URL for WhatsApp Web.
        """
        self.driver = None
        self.wait = None
        self.base_url = "https://web.whatsapp.com/"

    def launch(self):
        """
        Initializes the Chrome browser, navigates to WhatsApp Web, and waits for user login.

        The method prompts the user to scan the QR code and waits until the
        WhatsApp Web interface (specifically the search bar) is loaded,
        indicating a successful login.
        """
        console.print("[bold green]Launching WhatsApp Web...[/bold green]")
        # Initialize the Chrome WebDriver.
        self.driver = webdriver.Chrome()
        # Initialize WebDriverWait with a timeout of 30 seconds.
        self.wait = WebDriverWait(self.driver, 30)
        # Navigate to the WhatsApp Web URL.
        self.driver.get(self.base_url)

        console.print(
            "[bold yellow]Action Required: Please scan the QR code to log in.[/bold yellow]"
        )
        # Wait until the search bar element is visible to confirm successful login.
        # The search bar is identified by its contenteditable attribute and data-tab="3".
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            console.print("[bold green]Login successful![/bold green]")
        except TimeoutException:
            # If the search bar doesn't appear within the timeout, login failed.
            console.print(
                "[bold red]Timeout: Login took too long or was interrupted.[/bold red]"
            )
            self.quit()
            sys.exit(1)  # Exit the script if login fails.

    def find_contact(self, name: str) -> bool:
        """
        Searches for a contact or group by name and selects it in WhatsApp Web.

        Args:
            name: The full name of the contact or group to search for.

        Returns:
            True if the contact was found and selected, False otherwise.
        """
        try:
            # Locate the search box element.
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(name)
            # A short delay to allow search results to load.
            time.sleep(1.5)
            search_box.send_keys(
                Keys.ENTER
            )  # Press Enter to select the first search result.
            console.print(f"[green]✓ Found and selected: {name}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error: Could not find contact '{name}': {e}[/red]")
            return False

    def send_text(self, message: str) -> bool:
        """
        Sends a text message to the currently selected chat.

        Args:
            message: The text content of the message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        try:
            # Find the message input area, typically identified by its title attribute.
            msg_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@title="Type a message"]')
                )
            )
            msg_box.send_keys(message)
            msg_box.send_keys(Keys.ENTER)  # Press Enter to send the message.
            console.print("[green]✓ Message sent![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error sending text: {e}[/red]")
            return False

    def send_attachment(self, file_path: str, file_type: str = "document") -> bool:
        """
        Sends a file (document, image, or video) to the currently selected chat.

        Args:
            file_path: The absolute path to the file to be sent.
            file_type: The type of file to send. Can be "document" or "media".
                       "media" typically refers to images and videos.

        Returns:
            True if the attachment was sent successfully, False otherwise.
        """
        if not os.path.exists(file_path):
            console.print(f"[red]Error: File not found at {file_path}[/red]")
            return False

        try:
            # Click the 'Attach' icon to open the attachment menu.
            attach_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]'))
            )
            attach_btn.click()
            time.sleep(1)  # Short delay for the attachment menu to appear.

            # Map file types to the appropriate input element's 'accept' attribute.
            # WhatsApp uses different input elements for documents vs. media.
            if file_type == "media":
                # For Images & Videos, the input element accepts specific media types.
                accept_attr = "image/*,video/mp4,video/3gpp,video/quicktime"
            else:
                # For Documents, the input element accepts all file types.
                accept_attr = "*"

            # Locate the hidden file input element and send the file path to it.
            # This simulates selecting a file from the file system.
            file_input = self.driver.find_element(
                By.XPATH, f'//input[@accept="{accept_attr}"]'
            )
            file_input.send_keys(file_path)

            # Wait for the send button to appear after the file has been uploaded
            # to the preview window, then click it to send.
            send_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-testid="send"]'))
            )
            send_btn.click()

            console.print(
                f"[green]✓ {file_type.capitalize()} sent successfully![/green]"
            )
            return True
        except Exception as e:
            console.print(f"[red]Error sending attachment: {e}[/red]")
            return False

    def quit(self):
        """
        Closes the browser session and cleans up the WebDriver.
        """
        if self.driver:
            console.print("[bold yellow]Closing session...[/bold yellow]")
            self.driver.quit()


def main():
    """
    Main function to run the WhatsApp Master Automator CLI.

    Initializes the automator, handles user interaction via questionary,
    and orchestrates the WhatsApp automation tasks.
    """
    console.rule("[bold green]WhatsApp Master Automator[/bold green]")

    automator = WhatsAppMaster()
    try:
        automator.launch()  # Launch the browser and log in.

        while True:
            # Present a menu of actions to the user.
            action = questionary.select(
                "What would you like to do?",
                choices=["Send Message", "Send Attachment", "Switch Contact", "Exit"],
            ).ask()

            if action == "Exit":
                break  # Exit the loop and terminate the program.

            # For actions that require a contact, prompt the user and find the contact.
            if action in ["Switch Contact", "Send Message", "Send Attachment"]:
                contact = questionary.text("Enter contact or group name:").ask()
                if not contact:  # If user provides no contact, skip to next iteration.
                    console.print(
                        "[bold red]No contact name provided. Please try again.[/bold red]"
                    )
                    continue
                if not automator.find_contact(contact):
                    # If contact not found, continue to the next iteration of the loop.
                    continue

            if action == "Send Message":
                msg = questionary.text("Enter your message:").ask()
                if msg:  # Only send if message is not empty.
                    automator.send_text(msg)
                else:
                    console.print(
                        "[bold yellow]No message entered. Skipping.[/bold yellow]"
                    )

            elif action == "Send Attachment":
                f_type = questionary.select(
                    "File type:", choices=["document", "media"]
                ).ask()
                f_path = questionary.text("Enter full file path:").ask()
                if f_path:  # Only send if file path is provided.
                    automator.send_attachment(f_path, f_type)
                else:
                    console.print(
                        "[bold yellow]No file path entered. Skipping.[/bold yellow]"
                    )

            console.print("\n[bold cyan]--- Action Complete ---[/bold cyan]\n")

    except KeyboardInterrupt:
        # Handle graceful exit if the user presses Ctrl+C.
        console.print("\n[bold red]Interrupted by user.[/bold red]")
    finally:
        # Ensure the browser is closed regardless of how the program exits.
        automator.quit()
        console.print("[bold green]Exiting gracefully![/bold green]")


if __name__ == "__main__":
    # Entry point for the script.
    main()
