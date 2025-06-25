from flask import Blueprint, request, jsonify
from server.db.database import get_db
from server.services.notification_service import NotificationService

user_feedback_bp = Blueprint("user_feedback", __name__)

@user_feedback_bp.route("/feedback/like", methods=["POST"])
def like_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute("""
        INSERT INTO article_feedback (user_id, article_id, feedback_type)
        VALUES (%s, %s, 'like')
        ON DUPLICATE KEY UPDATE feedback_type = 'like'
    """, (user[0], article_id))

    conn.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "You liked this article."}), 200


@user_feedback_bp.route("/feedback/dislike", methods=["POST"])
def dislike_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute("""
        INSERT INTO article_feedback (user_id, article_id, feedback_type)
        VALUES (%s, %s, 'dislike')
        ON DUPLICATE KEY UPDATE feedback_type = 'dislike'
    """, (user[0], article_id))

    conn.commit()
    cursor.close()
    return jsonify({"status": "success", "message": "You disliked this article."}), 200


@user_feedback_bp.route("/articles/report", methods=["POST"])
def report_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        """
        INSERT INTO article_reports (user_id, article_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE article_id = article_id
        """,
        (user[0], article_id),
    )
    conn.commit()

    notifier = NotificationService()
    notifier.notify_admin_about_report(article_id, email)

    cursor.close()
    return jsonify({"status": "success", "message": "Article reported."})
