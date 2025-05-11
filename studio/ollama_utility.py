import requests

def analyze_text_with_phi3(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["response"]