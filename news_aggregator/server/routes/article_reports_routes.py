from flask import Blueprint, request, jsonify
from server.db.database import get_db

article_report_bp = Blueprint("article_report", __name__)

@article_report_bp.route("/articles/report", methods=["POST"])
def report_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")
    REPORT_THRESHOLD = 2

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user_id = user[0]

    try:
        cursor.execute(
            "INSERT INTO article_reports (user_id, article_id) VALUES (%s, %s)",
            (user_id, article_id)
        )
        conn.commit()
    except:
        return jsonify({"status": "error", "message": "You have already reported this article."}), 400

    cursor.execute("SELECT COUNT(*) FROM article_reports WHERE article_id = %s", (article_id,))
    report_count = cursor.fetchone()[0]

    if report_count >= REPORT_THRESHOLD:
        cursor.execute("UPDATE news_articles SET is_hidden = 1 WHERE id = %s", (article_id,))
        conn.commit()

    cursor.close()
    return jsonify({"status": "success", "message": "Article reported successfully."})
