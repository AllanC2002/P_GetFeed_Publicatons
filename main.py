import os
from flask import Flask, jsonify, request
import jwt
from dotenv import load_dotenv
from services.functions import start_consumer_thread, get_user_feed

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")

# Variable global para almacenar el token que usa el consumidor (puede mejorarse)
consumer_token = None

@app.route('/feed', methods=['GET'])
def feed():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401

    try:
        token = auth_header.split()[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = str(decoded.get("user_id"))
    except Exception as e:
        return jsonify({'error': f'Invalid token: {str(e)}'}), 403

    try:
        feed_publications = get_user_feed(user_id)
        return jsonify({"user_id": user_id, "feed": feed_publications}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch feed: {str(e)}"}), 500

if __name__ == '__main__':
    # Para arrancar el consumidor, pide el token de ambiente o ingresa uno aquí directamente
    consumer_token = os.getenv("CONSUMER_TOKEN")
    if not consumer_token:
        print("⚠️ WARNING: CONSUMER_TOKEN env var not set! The consumer thread might not work properly.")
    
    start_consumer_thread(consumer_token)
    app.run(host='0.0.0.0', port=8082, debug=True)
