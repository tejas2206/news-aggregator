from flask import Blueprint, request, jsonify
import logging
from server.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService(logger=logging.getLogger("auth_service"))


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    success, message = auth_service.signup(username, email, password)
    if success:
        return jsonify({"status": "success", "message": message}), 201
    else:
        return jsonify({"status": "error", "message": message}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    success, message, user = auth_service.login(email, password)
    if not success:
        return jsonify({"status": "error", "message": message}), 401
    return jsonify(
        {
            "status": "success",
            "message": message,
            "role": user["role"],
            "email": user["email"],
            "username": user["username"],
        }
    )
