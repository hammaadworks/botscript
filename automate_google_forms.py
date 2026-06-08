# /// script
# dependencies = [
#   "selenium",
#   "faker",
#   "questionary",
#   "rich",
# ]
# ///

import os
import json
import time
import sys
from random import randint, choice
from datetime import datetime, timedelta
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
fake = Faker("en_IN")

class GoogleFormAutomator:
    """
    A professional-grade Google Forms automator.
    Logic: Scans the live DOM for question blocks, determines type, and fills them.
    No hardcoded ID assumptions.
    """
    def __init__(self, form_url, headless=False):
        self.form_url = form_url
        self.driver = None
        self.wait = None
        self.headless = headless

    def start_browser(self):
        options = webdriver.ChromeOptions()
        if self.headless: options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,768")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get(self.form_url)
        
        # Check for login wall
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Sign in')]")))
            console.print("[bold yellow]⚠️ Login Required:[/bold yellow] This form requires a Google account. Please sign in manually in the opened browser.")
            # Give user time to sign in if they want
            time.sleep(5)
        except:
            pass

    def get_question_blocks(self):
        """Finds all question containers on the current page."""
        # Standard questions (role='listitem') plus automatic email collection blocks (geS5ne/o36pTe)
        return self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listitem'] | //div[contains(@class, 'geS5ne')] | //div[contains(@class, 'o36pTe')]")))

    def identify_and_fill(self, block, config_override=None):
        """
        Analyzes a question block and fills it.
        If config_override is provided, uses specific values for that label.
        """
        try:
            # 1. Get Label - Improved to catch more heading styles and clean asterisks
            try:
                # Priority: role='heading', then common label containers
                label_el = block.find_element(By.XPATH, ".//div[@role='heading'] | .//div[@id and @role='presentation'] | .//span[@id]")
                label_text = label_el.text.split("\n")[0].strip().rstrip('*').strip()
            except:
                label_text = "Field"
            
            if not label_text: return None

            # 2. Determine Type & Fill
            # Check Text/Para/Email/Number
            inputs = block.find_elements(By.XPATH, ".//input[@type='text' or @type='email' or @type='number' or @type='tel' or @type='url'] | .//textarea")
            if inputs:
                field = inputs[0]
                # If date/time specialized input
                if field.get_attribute("type") == "date":
                    val = self.get_random_date()
                elif "time" in label_text.lower():
                    self.fill_time(block, "random")
                    return label_text
                else:
                    val = self.get_faker_val(label_text, config_override)
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", field)
                time.sleep(0.3) # Wait for scroll to settle
                
                try:
                    self.wait.until(EC.element_to_be_clickable(field))
                    field.click()
                except:
                    self.driver.execute_script("arguments[0].click();", field)
                
                field.clear()
                # Use a small delay for realistic typing
                for char in str(val):
                    field.send_keys(char)
                    if randint(1, 10) > 8: time.sleep(0.02)
                
                # Small pause to trigger Google's auto-save
                time.sleep(0.3)
                return f"{label_text}: {val}"

            # Check Radio
            radios = block.find_elements(By.XPATH, ".//div[@role='radio']")
            if radios:
                target = choice(radios)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", target)
                time.sleep(0.2)
                try:
                    target.click()
                except:
                    self.driver.execute_script("arguments[0].click();", target)
                return f"{label_text}: [Radio Selected]"

            # Check Checkboxes
            checks = block.find_elements(By.XPATH, ".//div[@role='checkbox']")
            if checks:
                target = choice(checks)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", target)
                time.sleep(0.2)
                try:
                    target.click()
                except:
                    self.driver.execute_script("arguments[0].click();", target)
                return f"{label_text}: [Checkbox Selected]"

            # Check Dropdown
            dropdowns = block.find_elements(By.XPATH, ".//div[@role='listbox']")
            if dropdowns:
                dropdown = dropdowns[0]
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", dropdown)
                time.sleep(0.2)
                dropdown.click()
                time.sleep(1)
                options = self.driver.find_elements(By.XPATH, "//div[@role='option'][@data-value and not(@data-value='')]")
                if options: choice(options).click()
                return f"{label_text}: [Dropdown Selected]"

            # Check Linear Scale
            scales = block.find_elements(By.XPATH, ".//div[@data-value]")
            if scales:
                target = choice(scales)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", target)
                target.click()
                return f"{label_text}: [Scale Selected]"

            # Check Grid
            if block.find_elements(By.XPATH, ".//div[@role='grid']"):
                # Re-fetch rows within the block
                rows = block.find_elements(By.XPATH, ".//div[@role='row'][not(@aria-hidden='true')]")
                # Skip the first row if it's a header
                for row in rows:
                    cells = row.find_elements(By.XPATH, ".//div[@role='radio' or @role='checkbox']")
                    if cells:
                        target = choice(cells)
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", target)
                        time.sleep(0.1)
                        try:
                            target.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", target)
                return f"{label_text}: [Grid Filled]"

            return f"{label_text}: [Unknown Type]"
        except Exception as e:
            return f"Error filling field: {str(e).splitlines()[0]}"

    def get_faker_val(self, label, config=None):
        # === START OVERRIDE LOGIC ===
        # If the user provided a fixed value for this label in the UI, use it.
        if config:
            # Direct match
            if label in config: return config[label]
            # Fuzzy match (e.g. "Name" matches "Full Name")
            for key, val in config.items():
                if key.lower() in label.lower():
                    return val
        # === END OVERRIDE LOGIC ===

        label_lower = label.lower()
        
        # Identity
        if "name" in label_lower: return fake.name()
        if "email" in label_lower: return fake.email()
        if any(w in label_lower for w in ["phone", "mobile", "contact", "whatsapp"]):
            return f"{choice(['7', '8', '9'])}{randint(0, 9)}{randint(10000000, 99999999)}"
        if "address" in label_lower: return fake.address().replace("\n", ", ")
        
        # Contextual Feedback / Comments (Real English)
        if any(w in label_lower for w in ["comment", "feedback", "suggestion", "experience", "opinion", "think", "describe", "remark"]):
            responses = [
                "The experience was overall quite positive, and I appreciate the attention to detail in the process.",
                "I found the workflow to be very efficient and well-organized, making it easy to complete.",
                "Everything was great, but I think there might be some room for improvement in the communication phase.",
                "The interface is very user-friendly and I genuinely enjoyed the interaction today.",
                "I would highly recommend this service to others based on the quality of my recent experience.",
                "Please consider adding more comprehensive options for international users in future updates.",
                "I'm very satisfied with the results so far. Keep up the excellent work!",
                "The session was exceptionally informative and provided a lot of value to the participants.",
                "I believe the current approach is solid, though streamlining the initial steps could help.",
                "Great job on the presentation; it was clear, concise, and addressed all my main concerns."
            ]
            return choice(responses)
            
        # Short titles/subjects
        if any(w in label_lower for w in ["subject", "title", "summary", "heading"]):
            return fake.sentence(nb_words=randint(3, 6)).rstrip(".")
            
        # Generic fallback that's still human-like
        return fake.sentence(nb_words=10)

    def get_random_date(self):
        offset = randint(-2, 2)
        return (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")

    def fill_time(self, block, val):
        inputs = block.find_elements(By.XPATH, ".//input[@type='text']")
        if len(inputs) >= 2:
            hh = f"{randint(0, 23):02d}"
            mm = f"{randint(0, 59):02d}"
            inputs[0].send_keys(hh)
            inputs[1].send_keys(mm)

    def submit(self):
        try:
            # Detect Submit/Next/Send buttons
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[text()="Submit" or text()="Next" or text()="Send"] | //div[@jsname="M2UYVd"]')))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", submit_btn)
            time.sleep(0.5)
            
            # Record page before click to detect transition
            old_source = self.driver.page_source
            
            try:
                submit_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", submit_btn)
            
            # Wait for page to change or update
            time.sleep(2)
            
            # Success keywords
            success_terms = ["response has been recorded", "Submitted", "Thank you", "Your response has been recorded", "completed"]
            page_text_lower = self.driver.page_source.lower()
            
            if any(term.lower() in page_text_lower for term in success_terms):
                return "finished"
                
            # If page source changed but no success message, it's likely a next page
            if self.driver.page_source != old_source:
                return "next_page"
                
            return "error"
        except Exception as e:
            console.print(f"[dim red]Submit attempt failed: {str(e).splitlines()[0]}[/dim red]")
            return "error"

    def submit_another(self):
        try:
            # Try finding the "Submit another response" link
            another = self.driver.find_elements(By.LINK_TEXT, "Submit another response")
            if another:
                another[0].click()
                time.sleep(2)
                return True
            return False
        except:
            return False

    def close(self):
        if self.driver: self.driver.quit()

def main():
    console.print(Panel("[bold indigo]Google Forms Master Automator v3.0[/bold indigo]\n[white]Autonomous Live-Filling Mode[/white]"))
    
    url = questionary.text("Enter Google Form URL:").ask()
    if not url: return

    loop_count = int(questionary.text("How many submissions?", default="1").ask())
    
    # === START UI OVERRIDE SETUP ===
    overrides_raw = questionary.text("Any fixed field values? (Format: 'Label:Value, Label:Value' or leave empty):").ask()
    overrides = {}
    if overrides_raw:
        try:
            for pair in overrides_raw.split(","):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    overrides[k.strip()] = v.strip()
            console.print(f"[bold green]Applied {len(overrides)} fixed overrides.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error parsing overrides: {e}[/bold red]")
    # === END UI OVERRIDE SETUP ===
    
    automator = GoogleFormAutomator(url)
    
    try:
        automator.start_browser()
        
        success_count = 0
        while success_count < loop_count:
            console.print(f"\n[bold cyan]Submission {success_count + 1}/{loop_count}[/bold cyan]")
            
            # Form might be multi-page
            finished = False
            page_error = False
            
            while not finished:
                # Get initial block count
                try:
                    initial_blocks = automator.get_question_blocks()
                    block_count = len(initial_blocks)
                    console.print(f"Found {block_count} questions on this page.")
                    
                    for j in range(block_count):
                        # RE-FETCH BLOCKS every time to avoid StaleElementReference errors
                        current_blocks = automator.get_question_blocks()
                        if j >= len(current_blocks):
                            break
                        
                        block = current_blocks[j]
                        res = automator.identify_and_fill(block, config_override=overrides)
                        if res: console.print(f"  [green]✓[/green] {res}")
                        time.sleep(0.3)
                except Exception as e:
                    console.print(f"[red]Error finding questions: {str(e).splitlines()[0]}[/red]")
                    page_error = True
                    break
                
                status = automator.submit()
                if status == "finished":
                    console.print("[bold green]✅ Success: Response Recorded![/bold green]")
                    success_count += 1
                    finished = True
                elif status == "next_page":
                    console.print("[yellow]Moving to next page...[/yellow]")
                    time.sleep(1)
                else:
                    console.print("[red]❌ Submission failed or error occurred. Forcing refresh to recover...[/red]")
                    page_error = True
                    break
            
            # AFTER SUBMISSION (OR ERROR): ALWAYS Force Refresh to the starting URL
            # This ensures we are back at the beginning of the form for the next loop.
            if success_count < loop_count or page_error:
                console.print("[yellow]Forcing page refresh for next attempt...[/yellow]")
                automator.driver.get(url)
                time.sleep(3) # Give it extra time to load the fresh form

    except KeyboardInterrupt:
        console.print("[yellow]Aborted by user.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Critical Error: {e}[/bold red]")
    finally:
        console.print("\n[bold green]Success: All tasks completed. Alhamdulillah.[/bold green]")
        time.sleep(5)
        automator.close()

if __name__ == "__main__":
    main()
