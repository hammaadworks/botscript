# /// script
# dependencies = [
#   "google-generativeai",
#   "python-dotenv",
#   "black",
#   "isort",
#   "rich",
# ]
# ///

import os
import time
import logging
import subprocess
import sys
import google.generativeai as genai
import grpc
import atexit
import fnmatch
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt
from rich.theme import Theme

# Custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

console = Console(theme=custom_theme)

# Load environment variables
load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY = ""

# Suppress generic logging in favor of Rich UI
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Broad support for various languages (Formatting is currently Python-specific)
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".cs", ".go", ".rs", ".rb", ".php", ".html", ".css"}

def ensure_installed():
    for tool in ["black", "isort"]:
        try:
            subprocess.run([tool, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            console.print(f"[warning]Installing missing dependency:[/warning] {tool}...")
            subprocess.run([sys.executable, "-m", "pip", "install", tool, "--quiet"], check=True)

def configure_ai():
    if not GEMINI_API_KEY:
        console.print("[error]Error:[/error] GEMINI_API_KEY is not set in your .env file.")
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

model = configure_ai()

def shutdown_grpc():
    try:
        genai.shutdown()
    except Exception as e:
        logger.warning(f"Error during gRPC shutdown: {e}")


atexit.register(shutdown_grpc)

def read_gitignore(directory):
    """Read .gitignore and return a set of ignored files and folders."""
    gitignore_path = os.path.join(directory, ".gitignore")
    ignored = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    return ignored

def should_skip(file_path, ignored_patterns):
    """Check if a file should be skipped based on .gitignore."""
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    return False

def generate_docstring(code, ext):
    """Generate professional docstrings based on the file type."""
    prompt = f"""
    You are an expert developer. Add high-quality, professional docstrings/comments to this {ext} code:
    ```
    {code}
    ```
    Rules:
    1. Return ONLY the documented code enclosed within triple quotes (```).
    2. NEVER change the application logic.
    3. Follow clean code principles and the standard comment style for this language (e.g., Google style for Python, JSDoc for JS/TS).
    4. Do not include introductory or concluding conversational text.
    """
    retries = 3
    retry_delay = 2
    for attempt in range(retries):
        try:
            response = model.generate_content(
                prompt, generation_config=genai.GenerationConfig(max_output_tokens=8000, temperature=0.2)
            )
            return response.text.strip()
        except (grpc.RpcError, Exception) as e:
            if attempt < retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
    return code

def format_code(file_path):
    """Format Python code using black and isort."""
    if file_path.endswith(".py"):
        try:
            subprocess.run(["isort", file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["black", file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass # Silently fail formatting if syntax is broken

def process_file(file_path, progress, task_id):
    """Process a single file."""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            code = file.read()
        
        updated_code = generate_docstring(code, ext)
        
        # Robustly extract code from markdown backticks
        if "```" in updated_code:
            parts = updated_code.split("```")
            for part in parts:
                if len(part.strip()) > len(code) * 0.5:
                    # Strip language identifier if present (e.g., ```python)
                    first_line = part.strip().split('\n')[0]
                    if first_line.isalpha() and len(first_line) < 10:
                        updated_code = part.strip()[len(first_line):].strip()
                    else:
                        updated_code = part.strip()
                    break
        
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(updated_code)
        
        if ext == ".py":
            format_code(file_path)
            
        progress.update(task_id, advance=1)
        console.print(f"  [success]✓[/success] Documented & Formatted: [white]{os.path.basename(file_path)}[/white]")
        return True
    except Exception as e:
        progress.update(task_id, advance=1)
        console.print(f"  [error]✗[/error] Failed: [white]{os.path.basename(file_path)}[/white] ({e})")
        return False

def main():
    console.print(Panel.fit(
        "[bold highlight]AI Documentor Bot[/bold highlight]\n"
        "[white]Powered by Gemini 2.0 Flash[/white]",
        border_style="highlight"
    ))
    
    ensure_installed()
    
    target_path = Prompt.ask("[info]Enter file or folder path[/info]", default=".").strip()
    
    if not os.path.exists(target_path):
        console.print("[error]Error: The specified path does not exist.[/error]")
        return

    files_to_process = []
    
    # Identify files
    if os.path.isfile(target_path):
        if any(target_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            files_to_process.append(target_path)
    else:
        ignored_patterns = read_gitignore(target_path)
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d), ignored_patterns) and not d.startswith('.')]
            for file in files:
                file_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS) and not should_skip(file_path, ignored_patterns):
                    files_to_process.append(file_path)

    if not files_to_process:
        console.print("[warning]No supported files found to process.[/warning]")
        return

    console.print(f"\n[info]Found {len(files_to_process)} file(s) to process.[/info]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console
    ) as progress:
        process_task = progress.add_task("[cyan]Enhancing Codebase...", total=len(files_to_process))
        
        success_count = 0
        for file_path in files_to_process:
            if process_file(file_path, progress, process_task):
                success_count += 1
            time.sleep(1.5) # Rate limit protection

    console.print(Panel(
        f"[bold success]Alhamdulillah! Documentation Complete.[/bold success]\n"
        f"Successfully enhanced [highlight]{success_count}[/highlight] out of [highlight]{len(files_to_process)}[/highlight] files.",
        title="Summary",
        border_style="success"
    ))

if __name__ == "__main__":
    main()
