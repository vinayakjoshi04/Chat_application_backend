from flask import Blueprint, request, jsonify
from config import get_db_connection
import bcrypt
import sqlite3  # ✅ Import sqlite3

# Create a Blueprint
routes_bp = Blueprint("routes", __name__)

@routes_bp.route('/')
def home():
    return jsonify({"message": "Welcome to the Poco Backend API!"}), 200

# ---------------------- User Routes ----------------------

@routes_bp.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row  # ✅ Enable column name access
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        return jsonify([dict(user) for user in users]), 200
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@routes_bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    name, email, password = data.get("name"), data.get("email"), data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",  # ✅ Use `?` for SQLite
                       (name, email, hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return jsonify({"error": "User already exists or invalid data"}), 400
    finally:
        conn.close()

@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data.get("email"), data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row  # ✅ Use row_factory to access columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            return jsonify({"message": "Login successful!", "user_id": user["id"], "name": user["name"]}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": "Login error"}), 500
    finally:
        conn.close()

# ---------------------- Friend Request Routes ----------------------

@routes_bp.route('/friend-request', methods=['POST'])
def send_friend_request():
    data = request.json
    user_id, friend_id = data.get("user_id"), data.get("friend_id")

    if not all([user_id, friend_id]):
        return jsonify({"error": "Missing user_id or friend_id"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO friends (user_id, friend_id, status) VALUES (?, ?, 'pending')", 
                       (user_id, friend_id))
        conn.commit()
        return jsonify({"message": "Friend request sent!"}), 201
    except Exception as e:
        print(f"❌ Friend request error: {e}")
        return jsonify({"error": "Friend request failed"}), 400
    finally:
        conn.close()

@routes_bp.route('/friend-request/accept', methods=['POST'])
def accept_friend_request():
    data = request.json
    user_id, friend_id = data.get("user_id"), data.get("friend_id")

    if not all([user_id, friend_id]):
        return jsonify({"error": "Missing user_id or friend_id"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE friends SET status = 'accepted' WHERE user_id = ? AND friend_id = ? AND status = 'pending'", 
                       (friend_id, user_id))
        conn.commit()
        return jsonify({"message": "Friend request accepted!"}), 200
    except Exception as e:
        print(f"❌ Accept friend request error: {e}")
        return jsonify({"error": "Failed to accept friend request"}), 400
    finally:
        conn.close()

@routes_bp.route('/friends/<int:user_id>', methods=['GET'])
def get_friends(user_id):
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.email FROM users u
            JOIN friends f ON (u.id = f.friend_id OR u.id = f.user_id)
            WHERE (f.user_id = ? OR f.friend_id = ?) AND f.status = 'accepted' AND u.id != ?
        """, (user_id, user_id, user_id))

        friends = cursor.fetchall()
        return jsonify([dict(friend) for friend in friends]), 200
    except Exception as e:
        print(f"❌ Get friends error: {e}")
        return jsonify({"error": "Error fetching friends"}), 500
    finally:
        conn.close()

# ---------------------- Messaging Routes ----------------------

@routes_bp.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    sender_id, receiver_id, message = data.get("sender_id"), data.get("receiver_id"), data.get("message")

    if not all([sender_id, receiver_id, message]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)", 
                       (sender_id, receiver_id, message))
        conn.commit()
        return jsonify({"message": "Message sent!"}), 201
    except Exception as e:
        print(f"❌ Message sending error: {e}")
        return jsonify({"error": "Message sending failed"}), 400
    finally:
        conn.close()

@routes_bp.route('/messages/<int:user_id>/<int:friend_id>', methods=['GET'])
def get_messages(user_id, friend_id):
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sender_id, receiver_id, message, timestamp FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        """, (user_id, friend_id, friend_id, user_id))

        messages = cursor.fetchall()
        return jsonify([dict(msg) for msg in messages]), 200
    except Exception as e:
        print(f"❌ Fetch messages error: {e}")
        return jsonify({"error": "Error fetching messages"}), 500
    finally:
        conn.close()
