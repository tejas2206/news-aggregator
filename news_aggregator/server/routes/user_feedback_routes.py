from flask import Blueprint, request, jsonify
import logging
from server.services.user_feedback_service import UserFeedbackService

user_feedback_bp = Blueprint("user_feedback", __name__)
user_feedback_service = UserFeedbackService(
    logger=logging.getLogger("user_feedback_service")
)


@user_feedback_bp.route("/feedback/like", methods=["POST"])
def like_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")
    success, message = user_feedback_service.like_article(email, article_id)
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 400


@user_feedback_bp.route("/feedback/dislike", methods=["POST"])
def dislike_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")
    success, message = user_feedback_service.dislike_article(email, article_id)
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 400
