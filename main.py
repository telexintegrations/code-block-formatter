from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import re
import json
from bs4 import BeautifulSoup

app = FastAPI(title="Code Block Formatter")


class Setting(BaseModel):
    label: str
    type: str
    description: Optional[str] = None
    default: Any
    required: bool


class FormatRequest(BaseModel):
    channel_id: str
    settings: List[Setting]
    message: str


def get_setting_value(settings: List[Setting], label: str, default: Any) -> Any:
    """Extract setting value from settings list"""
    for setting in settings:
        if setting.label == label:
            return setting.default
    return default


def detect_language(code: str) -> str:
    """Detect programming language based on common patterns."""
    patterns = {
        'python': (
            r'(def |class |import |from .+ import|\s{4}|@decorator|async def|'
            r'print\(|if __name__ == "__main__":|raise Exception)'
        ),
        'javascript': (
            r'(const |let |var |function |=>|{.*}|console\.|document\.|'
            r'window\.|addEventListener|Promise|async function)'
        ),
        'typescript': r'(interface |type |namespace |enum |readonly |private |public |async )',
        'java': r'(public class |private |protected |void |static |extends |implements )',
        'html': r'(<[^>]+>|<!DOCTYPE|<html|<body|<head|<script|<style)',
        'css': r'(@media|@import|@keyframes|{.*}|margin:|padding:|color:|background:)',
        'sql': r'(SELECT |INSERT |UPDATE |DELETE |CREATE TABLE|ALTER |DROP |WHERE |JOIN )',
        'bash': r'(#!/bin/|echo |sudo |apt |yum |brew |chmod |chown |mkdir |cd |ls )',
        'json': r'^[\s]*({|\[)[\s\S]*?(}|\])[\s]*$',
        'xml': r'(<\?xml|<[^>]+>[\s\S]*?</[^>]+>)',
    }
    for lang, pattern in patterns.items():
        if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
            return lang
    return 'plaintext'


def is_code_block(text: str, min_lines: int) -> bool:
    """
    Determine if text is likely a code block
    """
    lines = text.split('\n')

    if len(lines) < min_lines:
        return False
     
    # Check for common code indicators
    code_indicators = [
        # Indentation patterns
        any(line.startswith(('    ', '\t')) for line in lines),
        # Common programming keywords
        any(keyword in text.lower() for keyword in [
            'function', 'def ', 'class ', 'import ', 'return', 'const ', 'let ',
            'var ', 'if ', 'for ', 'while ', 'try:', 'catch', 'public ', 'private '
        ]),
        # Brackets and parentheses patterns
        text.count('{') > 0 and text.count('}') > 0,
        text.count('(') > 0 and text.count(')') > 0,
        # Special characters common in code
        ';' in text or ':' in text,
        # Assignment operations
        '=' in text and not '==' in text,
        # Common code punctuation patterns
        re.search(r'[a-zA-Z0-9_]+\([^)]*\)', text) is not None,
    ]
    
    return sum(code_indicators) >= 2  # At least 2 indicators should be present


def format_code_blocks(text: str, settings: List[Setting]) -> str:
    """
    Detect and format code blocks with proper markdown syntax
    """
    # Get settings
    min_lines = int(get_setting_value(settings, "minLines", 2))
    detect_lang = get_setting_value(settings, "detectLanguage", True)
   
    # If already contains markdown code blocks, return as is
    if "```" in text:
        return text
      
    lines = text.split('\n')
  
    # Single line response, return as is
    if len(lines) < min_lines:
        return text
      
    # Check if text looks like code
    if not is_code_block(text, min_lines):
        return text
      
    # Detect language if enabled
    lang = detect_language(text) if detect_lang else 'plaintext'
   
    # Format with code block
    return f"```{lang}\n{text}\n```"


@app.post("/format-message")
async def format_message(request: FormatRequest):
    try:
        # Validate settings
        if not request.settings:
            raise HTTPException(status_code=400, detail="Settings are required")
           
        # Format the message
        formatted_text = format_code_blocks(request.message, request.settings)
       
        # Return in the expected format
        return {
            "event_name": "message_formatted",
            "message": formatted_text,
            "status": "success",
            "username": "code-formatter-bot"
        }
    except Exception as e:
        return {
            "event_name": "message_formatted",
            "message": request.message,  # Return original message on error
            "status": "error",
            "username": "code-formatter-bot",
            "error": str(e)
        }


@app.post("/webhook")
async def telex_webhook(request: Request):
    payload = await request.json()
    print("Received webhook:", json.dumps(payload, indent=2))

    # Validate required fields
    if "event_name" not in payload or "message" not in payload:
        raise HTTPException(status_code=422, detail="Missing required fields: 'event_name' or 'message'")
    
    event_name = payload.get("event_name")
    raw_message = payload.get("message", "")

    # Clean up the message from HTML tags
    soup = BeautifulSoup(raw_message, "html.parser")
    cleaned_message = soup.get_text("\n")

    # Detect language if required
    language = "plaintext"
    for setting in payload.get("settings", []):
        if setting["label"] == "detectLanguage" and setting["default"]:
            language = detect_language(cleaned_message)

    # If it's a message event, process it
    if event_name == "message_received":
        formatted_message = f"```{language}\n{cleaned_message}\n```"

        response = {
            "event_name": "message_formatted",
            "message": formatted_message,
            "status": "success",
            "username": "code-formatter-bot"
        }

        print("Sending response:", json.dumps(response, indent=2))
        return response

    return {"status": "ignored"}


@app.get("/")
async def home():
    return {"message": "Code Formatter API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# create route for integration.json
@app.get("/integration.json")
async def get_integration_json():
    try:
        with open('integration.json', 'r') as f:
            contents = json.load(f)
        return JSONResponse(contents)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="configuration not found")


# Handle invalid routes
@app.route("/{path:path}")
async def catch_all(path: str):
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

