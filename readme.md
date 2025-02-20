# Telex Code Block Formatter Integration

An automatic code block formatter integration for Telex that detects and properly formats code snippets in messages.

## Local Development

### Prerequisites

-   Python 3.8 or higher
-   pip (Python package manager)
-   Git

### Setup

1.  Clone the repository:

bash

Copy

`git clone https://github.com/telex_integrations/code-formatter cd code-formatter`

2.  Create and activate virtual environment:

bash

Copy

`python -m venv venv source venv/bin/activate # On Windows, use: venv\Scripts\activate`

3.  Install dependencies:

bash

Copy

`pip install -r requirements.txt`

4.  Run locally:

bash

Copy

`uvicorn main:app --reload`

### sample test
curl -X POST "http://localhost:8000/format-message"

 -H "Content-Type: application/json"

 -d '{

 "channel_id": "0192dd70-cdf1-7e15-8776-4fee4a78405e",

 "settings": [

 {"label": "minLines", "type": "number", "default": 2, "required": true},

 {"label": "detectLanguage", "type": "boolean", "default": true, "required": true}

 ],

 "message": "def hello_world():\n print(\"Hello World!\")"

 }' 

response
"event_name": "message_formatted",
  "message": "```python\ndef hello_world():\n    print(\"Hello World!\")\n```",
  "status": "success",
  "username": "code-formatter-bot"

Contributing
------------

Pull requests are welcome! For major changes, open an issue first to discuss proposed updates.

License
-------

MIT License