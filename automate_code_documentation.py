# /// script
# dependencies = [
#   "google-generativeai",
#   "python-dotenv",
#   "black",
#   "isort",
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

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)


# Ensure required tools are installed
def ensure_installed():
    for tool in ["black", "isort"]:
        try:
            subprocess.run(
                [tool, "--version"], check=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
        except FileNotFoundError:
            logger.info(f"Installing missing dependency: {tool}")
            subprocess.run([sys.executable, "-m", "pip", "install", tool], check=True)


# Configure AI Model
def configure_ai():
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set in .env file.")
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(model_name="gemini-2.0-flash-exp")


model = configure_ai()


def shutdown_grpc():
    """Ensure gRPC shuts down cleanly."""
    try:
        genai.shutdown()
    except Exception as e:
        logger.warning(f"Error during gRPC shutdown: {e}")


atexit.register(shutdown_grpc)


def read_gitignore(directory):
    """Read .gitignore and return a set of ignored files and folders."""
    gitignore_path = os.path.join(directory, ".gitignore")
    ignored_patterns = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)
    return ignored_patterns


def should_skip(file_path, ignored_patterns):
    """Check if a file should be skipped based on .gitignore."""
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
                os.path.basename(file_path), pattern
                ):
            return True
    return False


def generate_docstring(code):
    """Generate professional Google-style docstrings with retries."""
    prompt = f"""
    You are an expert developer. Add high-quality Google-style docstrings to this code:
    ```
    {code}
    ```
    Rule:
    1. Return the documented code enclosed within triple quotes.
    2. Never change the application logic.
    3. Follow clean code principles and best coding practices while formatting. 
    4. Only return the code and nothing else.
    """
    retries = 5
    retry_delay = 2  # Initial delay in seconds
    for attempt in range(retries):
        try:
            response = model.generate_content(
                prompt, generation_config=genai.GenerationConfig(
                    max_output_tokens=2000, temperature=0.5
                )
                )
            return response.text.strip()
        except (grpc.RpcError, Exception) as e:
            logger.error(f"AI call failed (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2.5  # Exponential backoff
    logger.error("Max retries reached. Skipping AI enhancement for this file.")
    return code


def format_code(file_path):
    """Format Python code using black and isort."""
    if file_path.endswith(".py"):
        try:
            subprocess.run(["black", file_path], check=True)
            subprocess.run(["isort", file_path], check=True)
            logger.info(f"Formatted: {file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Formatting error in {file_path}: {e}")


def process_file(file_path):
    """Process a file: generate docstrings and format it."""
    logger.info(f"Processing file: {file_path}")
    try:
        with open(file_path, "r") as file:
            code = file.read()
        updated_code = generate_docstring(code)
        
        # Robustly extract code from markdown backticks
        if "```" in updated_code:
            # Split by ``` and find the part that looks like code
            parts = updated_code.split("```")
            for part in parts:
                # Check if it's the code block (usually starts with 'python' or just the code)
                if part.strip().startswith("python"):
                    updated_code = part.replace("python", "", 1).strip()
                    break
                elif len(part.strip()) > len(code) * 0.5: # Heuristic for code block
                    updated_code = part.strip()
                    break
        
        with open(file_path, "w") as file:
            file.write(updated_code)
        format_code(file_path)
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")


def process_project(directory):
    """Process all supported code files in a project directory."""
    ignored_patterns = read_gitignore(directory)
    # supported_extensions = {".py", ".java", ".js", ".html", ".css"}
    supported_extensions = {".py"}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if
                   not should_skip(os.path.join(root, d), ignored_patterns)]
        for file in files:
            file_path = os.path.join(root, file)
            if any(
                    file.endswith(ext) for ext in supported_extensions
                    ) and not should_skip(file_path, ignored_patterns):
                process_file(file_path)
                time.sleep(1.5)  # Prevent rate limits


def main():
    """Main function to process a project directory."""
    ensure_installed()
    project_directory = input("Enter your project path (default: .): ").strip()
    if not project_directory:
        project_directory = "."
    if os.path.isdir(project_directory):
        process_project(project_directory)
        logger.info("Documentation and formatting complete!")
    else:
        logger.error("Invalid directory. Please check your input.")


if __name__ == "__main__":
    main()
    print("Alhamdulillah: formatting complete!!")
