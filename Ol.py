import ollama, requests

def _check_connextion():
    try:
        requests.get('http://localhost:11434')
        return True
    except Exception:
        return False

def get_models() -> list:
    if _check_connextion():
        return [model['model'] for model in ollama.list()["models"]]
    return []

def chat(data : dict):
    return ollama.chat(model=data['model'], messages=data['context'], options=data['options'])
