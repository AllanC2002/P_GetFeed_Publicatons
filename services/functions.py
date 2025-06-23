import os
import time
import threading
import requests
from conections.redis import conection_redis

SECRET_KEY = os.getenv("SECRET_KEY")

def decode_if_bytes(value):
    if isinstance(value, bytes):
        return value.decode()
    return value

def load_following_data_from_service(user_id, token):
    """Obtiene la lista de usuarios que sigue un user_id usando token para autorización"""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(
            "http://localhost:8081/following",
            params={"user_id": user_id},
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Error fetching following list for user {user_id}: {response.status_code}")
            return []

        data = response.json()
        following_list = data.get("following", [])
        print(f"📥 Lista de seguidos cargada para el usuario {user_id}: {[str(f['Id_User']) for f in following_list]}")
        return [str(f["Id_User"]) for f in following_list]

    except Exception as e:
        print(f"⚠️ Exception loading following list for user {user_id}: {e}")
        return []

def update_feed_for_followers(user_id, publication_id, token):
    following_list = load_following_data_from_service(user_id, token)

    if not following_list:
        print(f"⚠️ El usuario {user_id} no sigue a nadie o no se pudo cargar la lista.")
        return

    r = conection_redis()
    for follower_id in following_list:
        feed_key = f"feed:{follower_id}"
        r.lpush(feed_key, publication_id)
        r.ltrim(feed_key, 0, 99)
        print(f"✅ Añadida publicación {publication_id} al feed de {follower_id}")

def consume_publication_stream(token):
    r = conection_redis()
    last_id = '0-0'
    while True:
        try:
            entries = r.xread({'stream_user_publications': last_id}, count=10, block=5000)
            if entries:
                for stream, messages in entries:
                    stream_decoded = decode_if_bytes(stream)
                    for message_id, message in messages:
                        print(f"📨 Mensaje recibido del stream {stream_decoded}: {message}")

                        user_id = decode_if_bytes(message.get(b'user_id') or message.get('user_id'))
                        publication_id = decode_if_bytes(message.get(b'publication_id') or message.get('publication_id'))

                        if user_id and publication_id:
                            print(f"📌 user_id: {user_id}, publication_id: {publication_id}")
                            update_feed_for_followers(user_id, publication_id, token)
                            last_id = message_id
                        else:
                            print(f"⚠️ Mensaje malformado o incompleto: {message}")
            else:
                time.sleep(1)
        except Exception as e:
            print(f"❌ Error consuming stream: {e}")
            time.sleep(5)

def start_consumer_thread(token):
    thread = threading.Thread(target=consume_publication_stream, args=(token,), daemon=True)
    thread.start()
