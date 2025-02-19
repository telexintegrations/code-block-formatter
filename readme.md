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