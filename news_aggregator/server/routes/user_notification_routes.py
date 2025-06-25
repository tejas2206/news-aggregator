from flask import Blueprint, request, jsonify
from server.db.database import get_db

user_notification_bp = Blueprint("user_notifications", __name__)


@user_notification_bp.route("/notifications", methods=["GET"])
def view_notifications():
    email = request.args.get("email")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        "SELECT category, enabled FROM notifications WHERE user_id = %s", (user["id"],)
    )
    categories = cursor.fetchall()

    cursor.execute(
        "SELECT keyword FROM user_keywords WHERE user_id = %s AND enabled = 1",
        (user["id"],),
    )
    keywords = [row["keyword"] for row in cursor.fetchall()]

    cursor.close()
    return jsonify(
        {"status": "success", "categories": categories, "keywords": keywords}
    )


@user_notification_bp.route("/notifications/toggle", methods=["POST"])
def toggle_category():
    data = request.get_json()
    email = data.get("email")
    category = data.get("category")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        """
        INSERT INTO notifications (user_id, category, enabled)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE enabled = NOT enabled
    """,
        (user[0], category),
    )
    conn.commit()
    cursor.close()

    return jsonify(
        {"status": "success", "message": f"Toggled notification for {category}."}
    )


@user_notification_bp.route("/notifications/keyword", methods=["POST"])
def add_keyword():
    data = request.get_json()
    email = data.get("email")
    keyword = data.get("keyword")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        """
        INSERT IGNORE INTO user_keywords (user_id, keyword, enabled)
        VALUES (%s, %s, 1)
    """,
        (user[0], keyword),
    )
    conn.commit()
    cursor.close()

    return jsonify({"status": "success", "message": "Keyword added to alerts."})


@user_notification_bp.route("/notifications/keyword", methods=["DELETE"])
def delete_keyword():
    email = request.args.get("email")
    keyword = request.args.get("keyword")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        "DELETE FROM user_keywords WHERE user_id = %s AND keyword = %s",
        (user[0], keyword),
    )
    conn.commit()
    cursor.close()

    return jsonify({"status": "success", "message": "Keyword removed."})

@user_notification_bp.route("/notifications/history", methods=["GET"])
def get_notification_history():
    email = request.args.get("email")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute("""
        SELECT sn.message, sn.sent_at, na.title, na.url 
        FROM sent_notifications sn
        JOIN news_articles na ON sn.article_id = na.id
        WHERE sn.user_id = %s
        ORDER BY sn.sent_at DESC
    """, (user["id"],))

    notifications = cursor.fetchall()
    cursor.close()
    return jsonify({"status": "success", "notifications": notifications})
