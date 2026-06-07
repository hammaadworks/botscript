# Google Forms Master Automator v2.0

A professional-grade Selenium-based automator for Google Forms. Supports all field types and features an interactive configuration builder with automated field discovery.

## Features
- **Field Discovery:** Automatically scans the form to find questions and their internal `aria-labelledby` IDs.
- **Full Input Support:**
  - Short Answer & Paragraph (with Faker data support)
  - Multiple Choice & Checkboxes
  - Dropdowns (Listboxes)
  - Linear Scales (1-10)
  - Grids (Multiple Choice Grid & Checkbox Grid)
  - Date & Time
  - File Upload (via Google Drive picker)
- **Persistence:** Saves configurations to `form_config.json` for repeated use.
- **Stealth:** Uses advanced Selenium options to minimize bot detection.

## Prerequisites
- Python 3.8+
- Google Chrome installed
- Chrome Driver (handled automatically by modern Selenium/webdriver-manager)

## Installation
```bash
pip install selenium faker questionary rich
```

## Usage
1. **Interactive Mode:**
   Run the script and follow the prompts to scan a form and build a configuration.
   ```bash
   python automate_google_forms.py
   ```
2. **Automated Mode:**
   If a `form_config.json` exists, the script will ask if you want to use it.

## Configuration (JSON)
The `form_config.json` structure:
- `url`: The form URL.
- `loop`: Number of submissions.
- `fields`: Array of field objects.
  - `type`: text, radio, checkbox, dropdown, scale, grid, date, time.
  - `id`: The internal `aria-labelledby` ID (e.g., `i1`).
  - `option`/`options`: The text of the option(s) to select.

## Troubleshooting
- **Sign-in Required:** If a form requires Google Sign-in, you must manually sign in once in the browser window opened by the script (the script waits 15s by default) or use a profile.
- **Dynamic IDs:** While IDs like `i1` are usually stable for a specific form version, if the form is edited, you may need to re-run the "Scan" feature.
