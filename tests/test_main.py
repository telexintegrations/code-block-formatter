from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)


def test_webhook_formatting():
    response = client.post("/webhook", json={
        "event_name": "message_received",
        "message": "def hello_world():\n    print(\"Hello World!\")",
        "settings": [
            {"label": "minLines", "type": "number", "default": 1, "required": True},
            {"label": "detectLanguage", "type": "boolean", "default": True, "required": True}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["event_name"] == "message_formatted"
    assert "```python" in data["message"]


def test_invalid_request():
    response = client.post("/webhook", json={})
    print(response.json())  # Debug the response
    assert response.status_code == 422
