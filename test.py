import requests

login_data = {
    "User_mail": "allancorrea",
    "password": "1234"
}

login_url = "http://52.203.72.116:8080/login"
feed_url = "http://localhost:8080/feed"
#feed_url = "http://54.147.87.111:8080/feed"

login_response = requests.post(login_url, json=login_data)
if login_response.status_code != 200:
    print("❌ Login failed:", login_response.status_code, login_response.text)
    exit()

token = login_response.json().get("token")
if not token:
    print("❌ Token no recibido.")
    exit()

print("Token .")
headers = {
    "Authorization": f"Bearer {token}"
}

feed_response = requests.get(feed_url, headers=headers)
print("\n🔎 Status feed:", feed_response.status_code)

try:
    feed_data = feed_response.json()
    print("📥 Feed recibido:")
    for i, pub in enumerate(feed_data.get("feed", []), start=1):
        print(f"\n📌 Publicación #{i}")
        print("🆔 ID:", pub.get("publication_id"))
        print("👤 Autor:", pub.get("user_id"))
        print("📝 Text:", pub.get("text"))
        print("🗓 Date:", pub.get("datepublish"))
        if pub.get("image_base64"):
            print("🖼 Multimedia: Yes")
        else:
            print("🖼 Multimedia: No")
except Exception as e:
    print("❌ Error decoding JSON:", str(e))
    print("Raw content:", feed_response.text)
