from flask import Blueprint, request, jsonify
from server.db.database import get_db
import bcrypt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"status": "error", "message": "User already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
        (username, email, hashed, "user"),
    )
    conn.commit()
    cursor.close()

    return (
        jsonify({"status": "success", "message": "User registered successfully"}),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    return jsonify(
        {
            "status": "success",
            "message": "Login successful",
            "role": user["role"],
            "email": user["email"],
            "username": user["username"],
        }
    )
