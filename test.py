import requests

# Paso 1: Login
login_data = {
    "User_mail": "ascorread1",
    "password": "1234"
}

login_response = requests.post("http://localhost:8080/login", json=login_data)
if login_response.status_code != 200:
    print("Login failed:", login_response.text)
    exit()

token = login_response.json().get("token")
print("Token:", token)

# Paso 2: Obtener feed
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

feed_response = requests.get("http://localhost:8082/feed", headers=headers)

print("Status feed:", feed_response.status_code)
try:
    print("Feed response:", feed_response.json())
except Exception as e:
    print("Error decoding JSON:", str(e))
    print("Raw content:", feed_response.text)

# Paso 3 (opcional): Obtener lista de seguidos (following)
following_response = requests.get("http://localhost:8081/following", headers=headers)
print("Status following:", following_response.status_code)
try:
    print("Following response:", following_response.json())
except Exception as e:
    print("Error decoding JSON:", str(e))
    print("Raw content:", following_response.text)
