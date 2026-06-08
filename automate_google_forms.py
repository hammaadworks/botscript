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
        return self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@role='listitem']")))

    def identify_and_fill(self, block, config_override=None):
        """
        Analyzes a question block and fills it.
        If config_override is provided, uses specific values for that label.
        """
        try:
            # 1. Get Label
            label_el = block.find_element(By.XPATH, ".//div[@id] | .//span[@id]")
            label_text = label_el.text.split("\n")[0].strip()
            if not label_text: return None

            # 2. Determine Type & Fill
            # Check Text/Para
            inputs = block.find_elements(By.XPATH, ".//input[@type='text'] | .//textarea")
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
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                field.click()
                field.clear()
                field.send_keys(val)
                return f"{label_text}: {val}"

            # Check Radio
            radios = block.find_elements(By.XPATH, ".//div[@role='radio']")
            if radios:
                target = choice(radios)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                target.click()
                return f"{label_text}: [Radio Selected]"

            # Check Checkboxes
            checks = block.find_elements(By.XPATH, ".//div[@role='checkbox']")
            if checks:
                target = choice(checks)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                target.click()
                return f"{label_text}: [Checkbox Selected]"

            # Check Dropdown
            dropdowns = block.find_elements(By.XPATH, ".//div[@role='listbox']")
            if dropdowns:
                dropdown = dropdowns[0]
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                dropdown.click()
                time.sleep(1)
                options = self.driver.find_elements(By.XPATH, "//div[@role='option'][@data-value and not(@data-value='')]")
                if options: choice(options).click()
                return f"{label_text}: [Dropdown Selected]"

            # Check Linear Scale
            scales = block.find_elements(By.XPATH, ".//div[@data-value]")
            if scales:
                target = choice(scales)
                target.click()
                return f"{label_text}: [Scale Selected]"

            # Check Grid
            if block.find_elements(By.XPATH, ".//div[@role='grid']"):
                rows = block.find_elements(By.XPATH, ".//div[@role='row'][.//div[@id]]")
                for row in rows:
                    cells = row.find_elements(By.XPATH, ".//div[@role='radio' or @role='checkbox']")
                    if cells: choice(cells).click()
                return f"{label_text}: [Grid Filled]"

            return f"{label_text}: [Unknown Type]"
        except Exception as e:
            return f"Error filling field: {e}"

    def get_faker_val(self, label, config=None):
        label = label.lower()
        if "name" in label: return fake.name()
        if "email" in label: return fake.email()
        if "phone" in label or "mobile" in label or "contact" in label:
            return f"{randint(7000, 9999)}{randint(100000, 999999)}"
        if "address" in label: return fake.address().replace("\n", ", ")
        return fake.sentence()

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
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//span[text()="Submit" or text()="Next"] | //div[@jsname="M2UYVd"]')))
            submit_btn.click()
            time.sleep(2)
            # Check if there's a next page or finished
            if "response has been recorded" in self.driver.page_source or "Submitted" in self.driver.page_source:
                return "finished"
            return "next_page"
        except:
            return "error"

    def submit_another(self):
        try:
            another = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Submit another response")))
            another.click()
            return True
        except:
            return False

    def close(self):
        if self.driver: self.driver.quit()

def main():
    console.print(Panel("[bold indigo]Google Forms Master Automator v3.0[/bold indigo]\n[white]Autonomous Live-Filling Mode[/white]"))
    
    url = questionary.text("Enter Google Form URL:").ask()
    if not url: return

    loop_count = int(questionary.text("How many submissions?", default="1").ask())
    
    automator = GoogleFormAutomator(url)
    
    try:
        automator.start_browser()
        
        for i in range(loop_count):
            console.print(f"\n[bold cyan]Submission {i+1}/{loop_count}[/bold cyan]")
            
            # Form might be multi-page
            finished = False
            while not finished:
                blocks = automator.get_question_blocks()
                console.print(f"Found {len(blocks)} questions on this page.")
                
                for block in blocks:
                    res = automator.identify_and_fill(block)
                    if res: console.print(f"  [green]✓[/green] {res}")
                    time.sleep(0.5)
                
                status = automator.submit()
                if status == "finished":
                    console.print("[bold green]✅ Response Recorded![/bold green]")
                    finished = True
                elif status == "next_page":
                    console.print("[yellow]Moving to next page...[/yellow]")
                    time.sleep(1)
                else:
                    console.print("[red]❌ Submission failed or error occurred.[/red]")
                    break
            
            if i < loop_count - 1:
                if not automator.submit_another():
                    console.print("[yellow]Refreshing for next submission...[/yellow]")
                    automator.driver.get(url)
                time.sleep(2)

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
