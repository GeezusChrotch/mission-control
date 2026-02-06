#!/usr/bin/env python3
"""
Download email attachments from Microsoft Graph API and extract text.
"""
import os
import sys
import json
import base64
import urllib.request
import subprocess
from pathlib import Path

# Load token from cache
def load_token():
    token_path = Path.home() / ".config" / "clippy" / "token-cache.json"
    if token_path.exists():
        with open(token_path) as f:
            data = json.load(f)
            return data.get("graphToken") or data.get("token")
    return None

def download_attachment(message_id, attachment_id, output_path, token):
    """Download an attachment from Microsoft Graph."""
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments/{attachment_id}"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/json"
    })
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        # Check if contentBytes exists
        if "contentBytes" in data:
            content = base64.b64decode(data["contentBytes"])
            with open(output_path, "wb") as f:
                f.write(content)
            return True
        elif "contentLocation" in data:
            # Large attachment stored elsewhere
            print(f"Large attachment at: {data['contentLocation']}")
            return False
        else:
            print(f"No content found. Response keys: {list(data.keys())}")
            return False

def list_attachments(message_id, token):
    """List all attachments for a message."""
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token
    })
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        return data.get("value", [])

def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error extracting text: {e}"

if __name__ == "__main__":
    token = load_token()
    if not token:
        print("Error: No token found. Run clippy login first.")
        sys.exit(1)
    
    # Message ID from the performance report email
    message_id = "AAMkADQwOWUxMmEwLWMyYjMtNGRkMS04NWNlLTQxY2ViNDk3MmRiMQBGAAAAAAAS8Z-LVn2NS6PNgDLBgrvnBwAhtLC72QwLTbhyIvAjIjC2AAAAD5XxAAC8zZsEC8FURIjxddCuotoRAATYUk6RAAA="
    
    print("Listing attachments...")
    attachments = list_attachments(message_id, token)
    
    if not attachments:
        print("No attachments found.")
        sys.exit(1)
    
    for att in attachments:
        print(f"Found: {att.get('name', 'unnamed')} ({att.get('size', 0)} bytes)")
        att_id = att.get("id")
        
        output_path = Path(f"/tmp/{att.get('name', 'attachment.pdf')}")
        print(f"Downloading to {output_path}...")
        
        if download_attachment(message_id, att_id, output_path, token):
            print(f"Downloaded: {output_path}")
            
            if output_path.suffix.lower() == ".pdf":
                print("\nExtracting text...")
                text = extract_pdf_text(output_path)
                print("\n" + "="*60)
                print(text[:3000])  # First 3000 chars
                print("="*60)
        else:
            print("Failed to download attachment")
