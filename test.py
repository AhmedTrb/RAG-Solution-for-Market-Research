import requests
import json

# Replace with your actual API key
API_KEY = 'AIzaSyAVecBp5oOHIgB9cTRLwIulq-l9PdteA1g'

# API endpoint
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}'

# Payload
payload = {
    "contents": [
        {
            "parts": [
                {"text": "Can I get a free API key from google for developpers?"}
            ]
        }
    ]
}

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Print the response
if response.status_code == 200:
    result = response.json()
    try:
        text_output = result['candidates'][0]['content']['parts'][0]['text']
        print("Gemini says:", text_output)
    except (KeyError, IndexError):
        print("Unexpected response format:", result)
else:
    print("Error:", response.status_code, response.text)
