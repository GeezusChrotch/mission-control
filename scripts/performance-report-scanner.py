#!/usr/bin/env python3
"""
Automated Performance Report Scanner
Downloads PDF attachments from Outlook and extracts Audio/Sound section
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def load_clippy_token():
    """Load Microsoft auth token from clippy cache."""
    token_path = Path.home() / ".config" / "clippy" / "token-cache.json"
    if token_path.exists():
        with open(token_path) as f:
            data = json.load(f)
            return data.get("graphToken") or data.get("token")
    return None

def search_performance_reports():
    """Search Outlook for performance report emails."""
    token = load_clippy_token()
    if not token:
        print("Error: No auth token found")
        return []
    
    # Use clippy to search
    result = subprocess.run(
        ["./clippy-wrapper.sh", "mail", "-s", "Performance Report", "--limit", "10", "--json"],
        capture_output=True,
        text=True,
        cwd="/Users/Josh/clawd"
    )
    
    try:
        data = json.loads(result.stdout)
        return data.get("emails", [])
    except:
        return []

def download_with_playwright(email_url, download_path):
    """Use Playwright to download attachment from Outlook web."""
    script = f'''
const {{ chromium }} = require('playwright');

(async () => {{
    const browser = await chromium.launch({{ headless: false }});
    const context = await browser.newContext({{ 
        storageState: '{Path.home()}/.config/clippy/storage-state.json'
    }});
    const page = await context.newPage();
    
    try {{
        await page.goto('{email_url}', {{ waitUntil: 'networkidle', timeout: 30000 }});
        await page.waitForTimeout(3000);
        
        // Look for attachment link/button
        const attachment = await page.locator('[role="button"]:has-text("Performance Report"), a:has-text(".pdf")').first();
        if (await attachment.isVisible().catch(() => false)) {{
            const [download] = await Promise.all([
                page.waitForEvent('download'),
                attachment.click()
            ]);
            await download.saveAs('{download_path}');
            console.log('Downloaded: {download_path}');
        }} else {{
            console.log('No attachment found');
        }}
    }} catch (e) {{
        console.error('Error:', e.message);
    }} finally {{
        await browser.close();
    }}
}})();
'''
    
    # Save and run script
    script_path = "/tmp/download-script.js"
    with open(script_path, "w") as f:
        f.write(script)
    
    result = subprocess.run(
        ["node", script_path],
        capture_output=True,
        text=True,
        cwd="/Users/Josh/clawd"
    )
    return result.returncode == 0 and "Downloaded" in result.stdout

def extract_audio_section(pdf_path):
    """Extract Audio/Sound section from PDF."""
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True
    )
    
    text = result.stdout
    lines = text.split("\n")
    
    # Find Audio/Sound section
    audio_section = []
    in_audio_section = False
    
    for i, line in enumerate(lines):
        if "Audio" in line or "Sound" in line:
            in_audio_section = True
            audio_section.append(line)
        elif in_audio_section:
            # Check if we've reached next section (all caps or empty line after content)
            if line.strip() == "" and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and next_line.isupper():
                    break
            audio_section.append(line)
    
    return "\n".join(audio_section) if audio_section else "Audio/Sound section not found"

def update_apple_note(date, content):
    """Update Apple Note with extracted content."""
    note_script = f'''
tell application "Notes"
    set noteTitle to "Sweeney Todd - Performance Reports (Audio/Sound)"
    set noteContent to "Sweeney Todd - Performance Reports (Audio/Sound Section Catalog)

Date: {date}
Scan Time: {datetime.now().strftime("%I:%M %p")}

---

🎵 AUDIO/SOUND NOTES:
{content}

---

📋 NEXT SCAN: Tomorrow at 7:00 AM"
    
    try
        set existingNote to first note whose name is noteTitle
        set body of existingNote to noteContent
    on error
        make new note with properties {{name:noteTitle, body:noteContent}}
    end try
end tell
'''
    
    result = subprocess.run(
        ["osascript", "-e", note_script],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

if __name__ == "__main__":
    print("Scanning for Performance Reports...")
    reports = search_performance_reports()
    
    if not reports:
        print("No performance reports found")
        sys.exit(0)
    
    for report in reports:
        subject = report.get("subject", "")
        date = report.get("received", "Unknown")
        
        print(f"\nFound: {subject}")
        print(f"Date: {date}")
        
        # Download PDF
        download_path = f"/tmp/performance_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # TODO: Get actual email URL for download
        # For now, manual download required
        print(f"📎 Attachment needs manual download")
        print(f"   Save to: {download_path}")
        print(f"   Then run: python3 {__file__} --extract {download_path}")

