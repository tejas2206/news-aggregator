from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from server.services.user_article_service import UserArticleService
from server.db.database import get_db

user_article_bp = Blueprint("user_articles", __name__)
user_article_service = UserArticleService(
    logger=logging.getLogger("user_article_service")
)


@user_article_bp.route("/headlines/today", methods=["GET"])
def get_today_headlines():
    today = datetime.today().strftime("%Y-%m-%d")
    category = request.args.get("category")
    articles = user_article_service.get_headlines_by_range(today, today, category)
    return jsonify({"status": "success", "articles": articles})


@user_article_bp.route("/headlines/range", methods=["GET"])
def get_headlines_by_range():
    start_date = request.args.get("from")
    end_date = request.args.get("to")
    category = request.args.get("category")
    if not start_date or not end_date:
        return jsonify({"status": "error", "message": "Missing date range"}), 400
    articles = user_article_service.get_headlines_by_range(
        start_date, end_date, category
    )
    return jsonify({"status": "success", "articles": articles})


@user_article_bp.route("/articles/saved", methods=["GET"])
def view_saved_articles():
    email = request.args.get("email")
    articles = user_article_service.get_saved_articles(email)
    return jsonify({"status": "success", "articles": articles})


@user_article_bp.route("/articles/save", methods=["POST"])
def save_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")
    success, message = user_article_service.save_article(email, article_id)
    if success:
        return jsonify({"status": "success", "message": message}), 201
    else:
        return jsonify({"status": "error", "message": message}), 400


@user_article_bp.route("/articles/saved/<int:article_id>", methods=["DELETE"])
def delete_saved_article(article_id):
    email = request.args.get("email")
    success, message = user_article_service.delete_saved_article(email, article_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 400


@user_article_bp.route("/search", methods=["GET"])
def search_articles():
    query = request.args.get("q", "")
    start_date = request.args.get("from")
    end_date = request.args.get("to")
    sort_by = request.args.get("sort_by", "published_at")
    articles = user_article_service.search_articles(
        query, start_date, end_date, sort_by
    )
    return jsonify({"status": "success", "articles": articles})


@user_article_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = user_article_service.get_categories()
    return jsonify({"status": "success", "categories": categories})


@user_article_bp.route("/personalized", methods=["GET"])
def get_personalized_articles():
    email = request.args.get("email")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user_id = user["id"]

    cursor.execute(
        """
        SELECT category
        FROM notifications
        WHERE user_id = %s AND enabled = 1
    """,
        (user_id,),
    )
    enabled_categories = [row["category"] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT keyword
        FROM user_keywords
        WHERE user_id = %s AND enabled = 1
    """,
        (user_id,),
    )
    keywords = [row["keyword"] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT article_id
        FROM saved_articles
        WHERE user_id = %s
    """,
        (user_id,),
    )
    saved_article_ids = [row["article_id"] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT article_id
        FROM article_feedback
        WHERE user_id = %s AND feedback_type = 'like'
    """,
        (user_id,),
    )
    liked_article_ids = [row["article_id"] for row in cursor.fetchall()]

    sql = """
        SELECT DISTINCT 
            n.id, 
            n.title, 
            n.url, 
            c.name AS category,
            n.published_at
        FROM news_articles n
        LEFT JOIN categories c ON n.category_id = c.id
        WHERE 1=1
    """

    params = []
    conditions = []

    if enabled_categories:
        conditions.append("c.name IN (%s)" % ",".join(["%s"] * len(enabled_categories)))
        params.extend(enabled_categories)

    if keywords:
        keyword_conditions = []
        for kw in keywords:
            keyword_conditions.append("(n.title LIKE %s OR n.content LIKE %s)")
            params.extend([f"%{kw}%", f"%{kw}%"])
        conditions.append(" OR ".join(keyword_conditions))

    if saved_article_ids:
        conditions.append("n.id IN (%s)" % ",".join(["%s"] * len(saved_article_ids)))
        params.extend(saved_article_ids)

    if liked_article_ids:
        conditions.append("n.id IN (%s)" % ",".join(["%s"] * len(liked_article_ids)))
        params.extend(liked_article_ids)

    if conditions:
        sql += " AND (" + " OR ".join(conditions) + ")"

    sql += " ORDER BY n.published_at DESC LIMIT 20"

    cursor.execute(sql, params)
    articles = cursor.fetchall()
    cursor.close()

    return jsonify({"status": "success", "articles": articles})
