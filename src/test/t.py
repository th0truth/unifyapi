import requests

token = input(": ")

r = requests.get("http://127.0.0.0:8000/api/v1/students/me", headers={"Authorization": f"Bearer {token}"})

print(r.text)