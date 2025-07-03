import requests

# Step 1: Login to obtain JWT token
login_data = {
    "User_mail": "allan",
    "password": "1234"
}

login_url = "http://52.203.72.116:8080/login"
feed_url = "http://localhost:8082/feed"

login_response = requests.post(login_url, json=login_data)
if login_response.status_code != 200:
    print("❌ Login failed:", login_response.status_code, login_response.text)
    exit()

token = login_response.json().get("token")
if not token:
    print("Token was not received.")
    exit()

print("Token successfully obtained.")

# Step 2: Get user feed
headers = {
    "Authorization": f"Bearer {token}"
}

feed_response = requests.get(feed_url, headers=headers)
print("\n🔎 Feed status:", feed_response.status_code)

try:
    feed_data = feed_response.json()
    print("📥 Feed data received:")
    for i, pub in enumerate(feed_data.get("feed", []), start=1):
        print(f"\n📌 Publication #{i}")
        print("🆔 ID:", pub.get("publication_id"))
        print("👤 Author:", pub.get("user_id"))
        print("📝 Text:", pub.get("text"))
        print("🗓 Date:", pub.get("datepublish"))
        if pub.get("image_base64"):
            print("🖼 Multimedia: Yes")
        else:
            print("🖼 Multimedia: No")
except Exception as e:
    print("❌ Error decoding JSON:", str(e))
    print("Raw content:", feed_response.text)
