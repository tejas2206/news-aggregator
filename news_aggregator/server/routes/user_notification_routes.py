from flask import Blueprint, request, jsonify
import logging
from server.services.user_notification_service import UserNotificationService

user_notification_bp = Blueprint("user_notifications", __name__)
user_notification_service = UserNotificationService(
    logger=logging.getLogger("user_notification_service")
)


@user_notification_bp.route("/notifications", methods=["GET"])
def view_notifications():
    email = request.args.get("email")
    success, message, categories, keywords = (
        user_notification_service.get_notifications(email)
    )
    if not success:
        return jsonify({"status": "error", "message": message}), 404
    return jsonify(
        {"status": "success", "categories": categories, "keywords": keywords}
    )


@user_notification_bp.route("/notifications/toggle", methods=["POST"])
def toggle_category():
    data = request.get_json()
    email = data.get("email")
    category = data.get("category")
    success, message = user_notification_service.toggle_category(email, category)
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "message": message})


@user_notification_bp.route("/notifications/keyword", methods=["POST"])
def add_keyword():
    data = request.get_json()
    email = data.get("email")
    keyword = data.get("keyword")
    success, message = user_notification_service.add_keyword(email, keyword)
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "message": message})


@user_notification_bp.route("/notifications/keyword", methods=["DELETE"])
def delete_keyword():
    email = request.args.get("email")
    keyword = request.args.get("keyword")
    success, message = user_notification_service.delete_keyword(email, keyword)
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "message": message})


@user_notification_bp.route("/notifications/history", methods=["GET"])
def get_notification_history():
    email = request.args.get("email")
    success, message, notifications = (
        user_notification_service.get_notification_history(email)
    )
    if not success:
        return jsonify({"status": "error", "message": message}), 400
    return jsonify({"status": "success", "notifications": notifications})
