from flask import Flask, request, jsonify
import jwt
import os
from dotenv import load_dotenv
from services.functions import get_user_feed, start_consumer_thread

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")

# Iniciar el hilo consumidor del stream al arrancar la app
start_consumer_thread()

@app.route("/feed", methods=["GET"])
def get_feed():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token missing or invalid"}), 401

    token = auth_header.replace("Bearer ", "")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid token payload"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    feed = get_user_feed(user_id)
    return jsonify({"feed": feed}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
