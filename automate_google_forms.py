import os
import json
import time
from random import randint
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import questionary
from rich.console import Console
from rich.table import Table

console = Console()
fake = Faker("en_IN")

class GoogleFormAutomator:
    """
    A sophisticated Google Forms automator that can handle various field types
    using a configuration-driven approach.
    """
    def __init__(self, form_url):
        self.form_url = form_url
        self.driver = None
        self.wait = None

    def start_browser(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get(self.form_url)

    def fill_text_field(self, aria_label, value_type="faker", fixed_value=None):
        """Fills a short or long text field."""
        try:
            xpath = f'//input[@aria-labelledby="{aria_label}"] | //textarea[@aria-labelledby="{aria_label}"]'
            field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            
            if value_type == "faker":
                value = fake.name() if "name" in aria_label.lower() else fake.text(max_nb_chars=50)
            elif value_type == "fixed":
                value = fixed_value
            else:
                value = str(fixed_value)
                
            field.click()
            field.clear()
            field.send_keys(value)
            return value
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fill text field {aria_label}: {e}[/yellow]")
            return None

    def select_radio(self, ids):
        """Selects a random radio button from a list of IDs."""
        try:
            rand_id = ids[randint(0, len(ids) - 1)]
            element = self.wait.until(EC.element_to_be_clickable((By.ID, rand_id)))
            element.click()
            return rand_id
        except Exception as e:
            console.print(f"[yellow]Warning: Could not select radio {ids}: {e}[/yellow]")
            return None

    def select_level(self, value):
        """Selects a level in a linear scale (1-10)."""
        try:
            lev = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[@data-value="{value}"]')))
            lev.click()
            return value
        except Exception as e:
            console.print(f"[yellow]Warning: Could not select level {value}: {e}[/yellow]")
            return None

    def submit(self):
        """Submits the form."""
        try:
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@jsname="M2UYVd"]')))
            submit_btn.click()
            return True
        except Exception as e:
            console.print(f"[red]Error: Submission failed: {e}[/red]")
            return False

    def submit_another(self):
        """Clicks 'Submit another response'."""
        try:
            another = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Submit another response")))
            another.click()
            return True
        except Exception:
            return False

    def close(self):
        if self.driver:
            self.driver.quit()

def interactive_config():
    """Interactive CLI to build form configuration."""
    console.print("[bold indigo]Google Forms Master Automator[/bold indigo]\n")
    
    form_id = questionary.text("Enter Google Form ID or Full URL:").ask()
    if not form_id: return None
    
    if "docs.google.com" not in form_id:
        url = f"https://docs.google.com/forms/d/e/{form_id}/viewform"
    else:
        url = form_id

    fields = []
    while True:
        field_type = questionary.select(
            "Add a field to automate:",
            choices=["Text/TextArea", "Radio Buttons", "Linear Scale (1-10)", "Done"]
        ).ask()
        
        if field_type == "Done":
            break
            
        if field_type == "Text/TextArea":
            aria_id = questionary.text("Enter aria-labelledby ID (e.g., i1):").ask()
            val_type = questionary.select("Value type:", choices=["faker", "fixed"]).ask()
            fixed_val = None
            if val_type == "fixed":
                fixed_val = questionary.text("Enter fixed value:").ask()
            fields.append({"type": "text", "id": aria_id, "val_type": val_type, "fixed": fixed_val})
            
        elif field_type == "Radio Buttons":
            ids = questionary.text("Enter ID list comma-separated (e.g., i9,i12):").ask()
            fields.append({"type": "radio", "ids": [i.strip() for i in ids.split(",")]})
            
        elif field_type == "Linear Scale (1-10)":
            fields.append({"type": "scale"})

    loop_count = int(questionary.text("How many times to submit?", default="1").ask())
    
    return {"url": url, "fields": fields, "loop": loop_count}

def main():
    config = interactive_config()
    if not config: return

    automator = GoogleFormAutomator(config["url"])
    
    with console.status("[bold green]Automating Google Form...[/bold green]"):
        automator.start_browser()
        
        for i in range(config["loop"]):
            console.print(f"\n[bold cyan]Submission {i+1}/{config['loop']}[/bold cyan]")
            
            for field in config["fields"]:
                if field["type"] == "text":
                    automator.fill_text_field(field["id"], field["val_type"], field["fixed"])
                elif field["type"] == "radio":
                    automator.select_radio(field["ids"])
                elif field["type"] == "scale":
                    automator.select_level(randint(1, 10))
                time.sleep(0.5)
            
            if automator.submit():
                console.print("[green]✓ Submitted![/green]")
            
            if i < config["loop"] - 1:
                if not automator.submit_another():
                    console.print("[yellow]! Could not find 'Submit another' link. Stopping.[/yellow]")
                    break
                time.sleep(2)
        
    console.print("\n[bold green]Success: All tasks completed! Alhamdulillah.[/bold green]")
    time.sleep(2)
    automator.close()

if __name__ == "__main__":
    main()
