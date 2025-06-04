import requests

def get_ai_response(user_text):
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "phi",  # change to your model name
            "prompt": user_text,
            "stream": False
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get('response', '[No response]')
        else:
            return f"[Error {response.status_code}]: {response.text}"
    except Exception as e:
        return f"[Ollama Error]: {e}"
