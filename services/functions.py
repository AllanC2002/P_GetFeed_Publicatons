import os
import time
import threading
import json
from datetime import datetime, timedelta
from conections.redis import conection_redis

def decode_if_bytes(value):
    if isinstance(value, bytes):
        return value.decode()
    return value

def update_feed_for_followers(publication_data, followers_str):
    if not followers_str:
        print("⚠️ Field 'followers' is empty in the event, skipping.")
        return

    followers = [f.strip() for f in followers_str.split(",") if f.strip()]
    if not followers:
        print("⚠️ Parsed followers list is empty.")
        return

    r = conection_redis()
    publication_json = json.dumps(publication_data)
    pub_id = publication_data.get("publication_id")

    for follower_id in followers:
        try:
            feed_key = f"feed:{follower_id}"
            existing_feed = r.lrange(feed_key, 0, 99)

            already_exists = False
            for item in existing_feed:
                try:
                    item_str = item.decode() if isinstance(item, bytes) else str(item)
                    item_json = json.loads(item_str)
                    if item_json.get("publication_id") == pub_id:
                        already_exists = True
                        break
                except Exception:
                    continue  # Ignore if item is not valid JSON

            if already_exists:
                print(f"⚠️ Publication {pub_id} already exists in feed for user {follower_id}")
                continue

            r.lpush(feed_key, publication_json)
            r.ltrim(feed_key, 0, 99)
            print(f"✅ Publication added to feed of user {follower_id}")
        except Exception as e:
            print(f"❌ Error updating feed for user {follower_id}: {e}")

def get_user_feed(user_id):
    r = conection_redis()
    feed_key = f"feed:{user_id}"
    raw_items = r.lrange(feed_key, 0, 99)

    publications = []
    seen_ids = set()
    time_limit = datetime.utcnow() - timedelta(hours=24)

    for item in raw_items:
        try:
            item_str = item.decode() if isinstance(item, bytes) else str(item)
            pub = json.loads(item_str)

            pub_id = pub.get("publication_id")
            if not pub_id or pub_id in seen_ids:
                continue

            date = datetime.fromisoformat(pub.get("datepublish"))
            if date < time_limit:
                continue  # skip old publications

            seen_ids.add(pub_id)
            publications.append(pub)

        except Exception as e:
            print(f"⚠️ Invalid entry ignored in feed: {e} -> {item}")

    return publications

def consume_publication_stream():
    r = conection_redis()
    last_id = '0-0'
    print("🚀 Feed stream consumer started...")

    while True:
        try:
            entries = r.xread({'stream_user_publications': last_id}, count=10, block=10000)
            if entries:
                for stream, messages in entries:
                    stream_decoded = decode_if_bytes(stream)
                    for message_id, message in messages:
                        cleaned_message = dict(message)
                        cleaned_message.pop('image_base64', None)
                        print(f"📨 Message received from stream {stream_decoded}: {cleaned_message}")

                        publication_data = {
                            "user_id": decode_if_bytes(message.get(b'user_id') or message.get('user_id')),
                            "publication_id": decode_if_bytes(message.get(b'publication_id') or message.get('publication_id')),
                            "text": decode_if_bytes(message.get(b'text') or message.get('text')),
                            "image_base64": decode_if_bytes(message.get(b'image_base64') or message.get('image_base64')),
                            "content_type": decode_if_bytes(message.get(b'content_type') or message.get('content_type')),
                            "datepublish": decode_if_bytes(message.get(b'datepublish') or message.get('datepublish')),
                        }

                        followers_str = decode_if_bytes(message.get(b'followers') or message.get('followers'))

                        if publication_data["publication_id"] and followers_str:
                            update_feed_for_followers(publication_data, followers_str)
                            last_id = message_id
                        else:
                            print(f"⚠️ Incomplete or malformed message: {message}")
            else:
                time.sleep(1)
        except Exception as e:
            print(f"❌ Error reading from stream: {e}")
            time.sleep(10)

def start_consumer_thread():
    thread = threading.Thread(target=consume_publication_stream, daemon=True)
    thread.start()
