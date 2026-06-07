import os
import json
import time
import sys
from random import randint, choice
from datetime import datetime
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()
fake = Faker("en_IN")

class GoogleFormAutomator:
    """
    A comprehensive Google Forms automator that handles all field types:
    Text, Paragraph, Multiple Choice, Checkboxes, Dropdowns, Linear Scales,
    Grids (MC/Checkbox), Date, Time, and File Uploads.
    """
    def __init__(self, form_url, headless=False):
        self.form_url = form_url
        self.driver = None
        self.wait = None
        self.headless = headless

    def start_browser(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,1024")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # To avoid being blocked
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get(self.form_url)

    def fill_text(self, identifier, value, is_id=True):
        """Fills short/long text fields."""
        try:
            if is_id:
                xpath = f'//input[@aria-labelledby="{identifier}"] | //textarea[@aria-labelledby="{identifier}"]'
            else:
                xpath = f'//div[contains(text(), "{identifier}")]/ancestor::div[1]//input | //div[contains(text(), "{identifier}")]/ancestor::div[1]//textarea'
            
            field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
            time.sleep(0.2)
            field.click()
            field.clear()
            field.send_keys(value)
            return value
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fill text field {identifier}: {e}[/yellow]")
            return None

    def select_radio(self, aria_id, option_text):
        """Selects a radio button option by text or aria-label."""
        try:
            # Find the radio group first
            xpath = f"//div[@aria-labelledby='{aria_id}']//div[@role='radio'][contains(@aria-label, '{option_text}') or .//span[text()='{option_text}']]"
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.click()
            return option_text
        except Exception as e:
            console.print(f"[yellow]Warning: Could not select radio {option_text}: {e}[/yellow]")
            return None

    def select_checkboxes(self, aria_id, option_texts):
        """Selects multiple checkboxes."""
        results = []
        for text in option_texts:
            try:
                xpath = f"//div[@aria-labelledby='{aria_id}']//div[@role='checkbox'][contains(@aria-label, '{text}') or .//span[text()='{text}']]"
                checkbox = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                if checkbox.get_attribute("aria-checked") == "false":
                    checkbox.click()
                results.append(text)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not select checkbox {text}: {e}[/yellow]")
        return results

    def select_dropdown(self, aria_id, option_text):
        """Selects an option from a dropdown."""
        try:
            dropdown = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[@role="listbox"][@aria-labelledby="{aria_id}"]')))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
            dropdown.click()
            time.sleep(0.8)
            
            option = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//div[@role="option"]//span[text()="{option_text}" or contains(text(), "{option_text}")]')))
            option.click()
            time.sleep(0.5)
            return option_text
        except Exception as e:
            console.print(f"[yellow]Warning: Could not select dropdown {option_text}: {e}[/yellow]")
            return None

    def select_scale(self, aria_id, value):
        """Selects a level in a linear scale."""
        try:
            xpath = f'//div[@aria-labelledby="{aria_id}"]//div[@data-value="{value}"]'
            lev = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lev)
            lev.click()
            return value
        except Exception as e:
            console.print(f"[yellow]Warning: Could not select scale value {value}: {e}[/yellow]")
            return None

    def fill_grid(self, row_aria_id, col_label):
        """Fills a row in a Grid (MC or Checkbox)."""
        try:
            # row_aria_id is the id of the row header or the row container
            xpath = f"//div[@role='row'][.//div[@id='{row_aria_id}']]//div[@role='radio' or @role='checkbox'][contains(@aria-label, '{col_label}')]"
            option = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
            option.click()
            return col_label
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fill grid row {row_aria_id}: {e}[/yellow]")
            return None

    def fill_date(self, aria_id, date_str):
        """Fills a date field (YYYY-MM-DD)."""
        try:
            field = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//input[@type="date"][@aria-labelledby="{aria_id}"]')))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
            field.send_keys(date_str)
            return date_str
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fill date: {e}[/yellow]")
            return None

    def fill_time(self, aria_id, time_val):
        """Fills a time field (HH:MM)."""
        try:
            inputs = self.driver.find_elements(By.XPATH, f'//div[@aria-labelledby="{aria_id}"]//input[@type="text"]')
            if len(inputs) >= 2:
                hh, mm = time_val.split(":")
                inputs[0].clear()
                inputs[0].send_keys(hh)
                inputs[1].clear()
                inputs[1].send_keys(mm)
                return time_val
            return None
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fill time: {e}[/yellow]")
            return None

    def upload_file(self, question_text, file_path):
        """Uploads a file."""
        try:
            btn_xpath = f"//div[contains(@aria-label, '{question_text}')]//span[text()='Add file'] | //span[text()='Add file']"
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
            btn.click()
            time.sleep(3)
            
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "picker-frame")))
            file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(os.path.abspath(file_path))
            
            time.sleep(2)
            try:
                upload_btn = self.driver.find_element(By.XPATH, "//div[@role='button']//div[text()='Upload']")
                upload_btn.click()
            except:
                pass
                
            self.driver.switch_to.default_content()
            self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "picker-frame")))
            return file_path
        except Exception as e:
            console.print(f"[yellow]Warning: File upload failed: {e}[/yellow]")
            self.driver.switch_to.default_content()
            return None

    def submit(self):
        """Submits the form."""
        try:
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[text()="Submit"] | //div[@jsname="M2UYVd"]')))
            submit_btn.click()
            # Wait for confirmation
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'recorded')] | //div[contains(text(), 'Submitted')]")))
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

    def scan_form(self):
        """Scans the form and returns a list of fields."""
        console.print("[bold cyan]Scanning Form Structure...[/bold cyan]")
        items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
        detected = []
        for item in items:
            try:
                label_el = item.find_element(By.XPATH, ".//div[@id] | .//span[@id]")
                label_text = label_el.text.split("\n")[0]
                aria_id = label_el.get_attribute("id")
                
                ftype = "text"
                options = []
                
                if item.find_elements(By.XPATH, ".//div[@role='radio']"):
                    ftype = "radio"
                    opts = item.find_elements(By.XPATH, ".//div[@role='radio']")
                    options = [o.get_attribute("aria-label") or o.text for o in opts]
                elif item.find_elements(By.XPATH, ".//div[@role='checkbox']"):
                    ftype = "checkbox"
                    opts = item.find_elements(By.XPATH, ".//div[@role='checkbox']")
                    options = [o.get_attribute("aria-label") or o.text for o in opts]
                elif item.find_elements(By.XPATH, ".//div[@role='listbox']"):
                    ftype = "dropdown"
                elif item.find_elements(By.XPATH, ".//div[@data-value]"):
                    ftype = "scale"
                elif item.find_elements(By.XPATH, ".//div[@role='grid']"):
                    ftype = "grid"
                    # Grid needs special handling for rows
                    rows = item.find_elements(By.XPATH, ".//div[@role='row'][.//div[@id]]")
                    for row in rows:
                        row_header = row.find_element(By.XPATH, ".//div[@id]")
                        detected.append({
                            "type": "grid",
                            "label": f"{label_text} ({row_header.text})",
                            "id": row_header.get_attribute("id"),
                            "parent_label": label_text
                        })
                    continue # Skip general grid add
                elif item.find_elements(By.XPATH, ".//input[@type='date']"):
                    ftype = "date"
                elif "time" in label_text.lower():
                    ftype = "time"
                
                detected.append({"type": ftype, "label": label_text, "id": aria_id, "options": options})
            except:
                continue
        return detected

def interactive_config():
    """Builds a configuration interactively."""
    console.print(Panel("[bold indigo]Google Forms Master Automator[/bold indigo]"))
    
    url = questionary.text("Enter Google Form URL:").ask()
    if not url: return None

    automator = GoogleFormAutomator(url)
    try:
        automator.start_browser()
        detected = automator.scan_form()
        automator.close()
    except Exception as e:
        console.print(f"[red]Error during scan: {e}[/red]")
        return None

    table = Table(title="Detected Fields")
    table.add_column("#", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Question", style="green")
    table.add_column("ID", style="yellow")
    
    for i, field in enumerate(detected):
        table.add_row(str(i+1), field["type"], field["label"], field["id"])
    
    console.print(table)
    
    selected_indices = questionary.checkbox(
        "Select fields to automate:",
        choices=[{"name": f"{f['label']} ({f['type']})", "value": i} for i, f in enumerate(detected)]
    ).ask()
    
    config_fields = []
    for idx in selected_indices:
        field = detected[idx]
        f_config = {"type": field["type"], "id": field["id"], "label": field["label"]}
        
        if field["type"] == "text":
            val_type = questionary.select(f"Value for '{field['label']}':", choices=["faker_name", "faker_email", "faker_sentence", "fixed"]).ask()
            f_config["val_type"] = val_type
            if val_type == "fixed":
                f_config["fixed"] = questionary.text("Enter fixed value:").ask()
        elif field["type"] in ["radio", "dropdown", "grid"]:
            f_config["option"] = questionary.text(f"Option for '{field['label']}':").ask()
        elif field["type"] == "checkbox":
            opts = questionary.text(f"Options for '{field['label']}' (comma-separated):").ask()
            f_config["options"] = [o.strip() for o in opts.split(",")]
        elif field["type"] == "scale":
            f_config["value"] = questionary.text(f"Value (1-10) for '{field['label']}':", default="random").ask()
        elif field["type"] == "date":
            f_config["value"] = questionary.text(f"Date for '{field['label']}' (YYYY-MM-DD):", default="today").ask()
        elif field["type"] == "time":
            f_config["value"] = questionary.text(f"Time for '{field['label']}' (HH:MM):", default="10:00").ask()
            
        config_fields.append(f_config)

    loops = int(questionary.text("How many submissions?", default="1").ask())
    config = {"url": url, "fields": config_fields, "loop": loops}
    
    with open("form_config.json", "w") as f:
        json.dump(config, f, indent=4)
    console.print("[green]Config saved to form_config.json[/green]")
    return config

def main():
    config = None
    if os.path.exists("form_config.json") and questionary.confirm("Use existing form_config.json?").ask():
        with open("form_config.json", "r") as f:
            config = json.load(f)
    else:
        config = interactive_config()
        
    if not config: return

    automator = GoogleFormAutomator(config["url"])
    try:
        automator.start_browser()
        for i in range(config["loop"]):
            console.print(f"\n[bold cyan]Submission {i+1}/{config['loop']}[/bold cyan]")
            for field in config["fields"]:
                ftype = field["type"]
                fid = field["id"]
                
                if ftype == "text":
                    val = ""
                    if field["val_type"] == "faker_name": val = fake.name()
                    elif field["val_type"] == "faker_email": val = fake.email()
                    elif field["val_type"] == "faker_sentence": val = fake.sentence()
                    else: val = field["fixed"]
                    automator.fill_text(fid, val)
                elif ftype == "radio":
                    automator.select_radio(fid, field["option"])
                elif ftype == "checkbox":
                    automator.select_checkboxes(fid, field["options"])
                elif ftype == "dropdown":
                    automator.select_dropdown(fid, field["option"])
                elif ftype == "scale":
                    val = randint(1, 5) if field["value"] == "random" else int(field["value"])
                    automator.select_scale(fid, val)
                elif ftype == "grid":
                    automator.fill_grid(fid, field["option"])
                elif ftype == "date":
                    val = datetime.now().strftime("%Y-%m-%d") if field["value"] == "today" else field["value"]
                    automator.fill_date(fid, val)
                elif ftype == "time":
                    automator.fill_time(fid, field["value"])
                
                time.sleep(0.3)
            
            if automator.submit():
                console.print("[green]✓ Submitted![/green]")
            
            if i < config["loop"] - 1:
                if not automator.submit_another():
                    automator.driver.get(config["url"])
                time.sleep(2)
                
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    finally:
        console.print("\n[bold green]Done. Alhamdulillah.[/bold green]")
        time.sleep(3)
        automator.close()

if __name__ == "__main__":
    main()
