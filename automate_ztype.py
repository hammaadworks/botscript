# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "opencv-python",
#   "easyocr",
#   "numpy",
#   "selenium",
#   "rich",
#   "typer",
# ]
# ///

import time
import cv2
import easyocr
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Z-Type Game Bot: Dominate the game with Computer Vision and OCR.")
console = Console()

SKIP_WORDS = ['ztype', 'new game', 'settings', 'my stats',
              'phoboslab', 'load your own text', 'wave', 'score']
ENGLISH_ALPHA = "thequickbrownfoxjumpedoverthelazydog"

class ZTypeBot:
    def __init__(self):
        self.prev_result = []
        self.reader = None
        self.driver = None
        self.canvas = None
        self.actions = None
    
    def init_ocr(self):
        with console.status("[bold cyan]Initializing EasyOCR model (this may take a moment)...[/bold cyan]"):
            self.reader = easyocr.Reader(['en'], detector='dbnet18') 
            console.print("[bold green]✓ EasyOCR initialized successfully![/bold green]")

    def init_browser(self):
        with console.status("[bold cyan]Opening browser and loading ZType...[/bold cyan]"):
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-infobars")
            options.add_argument("--window-size=800,1000")
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://zty.pe/")
            
            # Wait for canvas to be present
            self.canvas = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ztype-game-canvas"))
            )
            self.actions = ActionChains(self.driver)
            console.print("[bold green]✓ Browser launched and game loaded![/bold green]")

    def start_game(self):
        console.print("[bold yellow]Starting the game...[/bold yellow]")
        # Focus the body to ensure keystrokes register
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.click()
        time.sleep(1)
        self.actions.send_keys('new game').perform()
        time.sleep(2) # Wait for animation to finish

    def process_image(self, png_bytes):
        # Decode image from bytes
        nparr = np.frombuffer(png_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Resize using cv2
        img = cv2.resize(img, (500, 800), interpolation=cv2.INTER_LANCZOS4)
        
        # Color transform
        img[np.where((img < [100, 100, 100]).all(axis=2))] = [0, 0, 0]
        img[np.where((img >= [100, 100, 100]).all(axis=2))] = [225, 225, 225]
        
        return img

    def get_ocr_result(self, img) -> list[str]:
        # Read text from numpy array
        result = self.reader.readtext(img, detail=0, batch_size=8)
        result = [block.lower() for block in result if not block.lower().startswith(tuple(SKIP_WORDS))]
        result.sort(key=len)

        # Handle stuck letters
        if len(self.prev_result):
            self.prev_result.sort(key=len, reverse=True)
            
        for prev_word in self.prev_result:
            if prev_word in result:
                result.clear()
                result.append(ENGLISH_ALPHA)
        
        return result

    def play(self):
        console.print(Panel("[bold green]Bot is now playing![/bold green]\n"
                            "Watch it dominate or press [bold red]Ctrl+C[/bold red] in this terminal to stop."))
        
        try:
            while True:
                # Capture canvas directly
                png_bytes = self.canvas.screenshot_as_png
                img = self.process_image(png_bytes)
                
                ocr_result = self.get_ocr_result(img)
                self.prev_result = ocr_result
                
                if ocr_result:
                    words_str = ", ".join(ocr_result)
                    console.print(f"[cyan]Detected & Typing:[/cyan] [bold white]{words_str}[/bold white]")
                    for word in ocr_result:
                        self.actions.send_keys(word).perform()
                        time.sleep(0.05) # Small delay
                else:
                    console.print("[dim]No words detected...[/dim]")
                    time.sleep(0.3)
                    
        except KeyboardInterrupt:
            console.print("\n[bold magenta]Bot stopped by user. Closing browser...[/bold magenta]")
        finally:
            if self.driver:
                self.driver.quit()

@app.command()
def main():
    """Start the Z-Type Bot."""
    console.print(Panel.fit("[bold cyan]🤖 Z-Type Automation Bot[/bold cyan]\n"
                            "[italic]By @hammaadworks[/italic]", border_style="cyan"))
    
    bot = ZTypeBot()
    bot.init_ocr()
    bot.init_browser()
    bot.start_game()
    bot.play()

if __name__ == "__main__":
    app()
