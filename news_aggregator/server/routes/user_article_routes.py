from flask import Blueprint, request, jsonify
from server.db.database import get_db
from datetime import datetime

user_article_bp = Blueprint("user_articles", __name__)


@user_article_bp.route("/headlines/today", methods=["GET"])
def get_today_headlines():
    today = datetime.today().strftime("%Y-%m-%d")
    category = request.args.get("category")
    return get_headlines_by_range_internal(today, today, category)


@user_article_bp.route("/headlines/range", methods=["GET"])
def get_headlines_by_range():
    start_date = request.args.get("from")
    end_date = request.args.get("to")
    category = request.args.get("category")
    if not start_date or not end_date:
        return jsonify({"status": "error", "message": "Missing date range"}), 400
    return get_headlines_by_range_internal(start_date, end_date, category)


def get_headlines_by_range_internal(start, end, category="all"):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT keyword FROM blocked_keywords")
    keywords = [row["keyword"] for row in cursor.fetchall()]

    blocked_clauses = []
    blocked_params = []
    for keyword in keywords:
        blocked_clauses.append("(n.title NOT LIKE %s AND n.content NOT LIKE %s)")
        blocked_params.extend([f"%{keyword}%", f"%{keyword}%"])

    query = """
        SELECT n.id, n.title, n.url, c.name as category
        FROM news_articles n
        LEFT JOIN categories c ON n.category_id = c.id
        WHERE DATE(n.published_at) BETWEEN %s AND %s
    """
    query_params = [start, end]

    if category != "all":
        query += " AND c.name = %s"
        query_params.append(category)

    query += " AND n.is_hidden = 0 AND (c.hidden = 0 OR c.hidden IS NULL)"

    if blocked_clauses:
        query += " AND " + " AND ".join(blocked_clauses)
        query_params.extend(blocked_params)

    query += " ORDER BY n.published_at DESC LIMIT 20"

    cursor.execute(query, query_params)
    rows = cursor.fetchall()
    cursor.close()

    return jsonify({"status": "success", "articles": rows})

@user_article_bp.route("/articles/saved", methods=["GET"])
def view_saved_articles():
    email = request.args.get("email")
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT sa.article_id, na.title, na.url, na.content, c.name as category
        FROM saved_articles sa
        JOIN users u ON sa.user_id = u.id
        JOIN news_articles na ON sa.article_id = na.id
        LEFT JOIN categories c ON na.category_id = c.id
        WHERE u.email = %s
    """,
        (email,),
    )
    articles = cursor.fetchall()
    cursor.close()
    return jsonify({"status": "success", "articles": articles})


@user_article_bp.route("/articles/save", methods=["POST"])
def save_article():
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
        "INSERT INTO saved_articles (user_id, article_id) VALUES (%s, %s)",
        (user[0], article_id),
    )
    conn.commit()
    cursor.close()

    return (
        jsonify({"status": "success", "message": f"Article {article_id} saved."}),
        201,
    )


@user_article_bp.route("/articles/saved/<int:article_id>", methods=["DELETE"])
def delete_saved_article(article_id):
    email = request.args.get("email")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    cursor.execute(
        "DELETE FROM saved_articles WHERE user_id = %s AND article_id = %s",
        (user[0], article_id),
    )
    conn.commit()
    cursor.close()

    return jsonify(
        {
            "status": "success",
            "message": f"Article {article_id} deleted from saved list.",
        }
    )


@user_article_bp.route("/search", methods=["GET"])
def search_articles():
    query = request.args.get("q", "")
    start_date = request.args.get("from")
    end_date = request.args.get("to")
    sort_by = request.args.get("sort_by", "published_at")

    sql = """
        SELECT
            na.id,
            na.title,
            na.url,
            na.content,
            na.source,
            na.published_at,
            c.name AS category,
            COALESCE(SUM(CASE WHEN af.feedback_type = 'like' THEN 1 ELSE 0 END), 0) AS likes,
            COALESCE(SUM(CASE WHEN af.feedback_type = 'dislike' THEN 1 ELSE 0 END), 0) AS dislikes
        FROM news_articles na
        LEFT JOIN categories c ON na.category_id = c.id
        LEFT JOIN article_feedback af ON na.id = af.article_id
        WHERE (na.title LIKE %s OR na.content LIKE %s)
    """

    params = [f"%{query}%", f"%{query}%"]

    if start_date and end_date:
        sql += " AND DATE(na.published_at) BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    sql += " GROUP BY na.id "

    if sort_by == "likes":
        sql += " ORDER BY likes DESC"
    elif sort_by == "dislikes":
        sql += " ORDER BY dislikes DESC"
    else:
        sql += " ORDER BY na.published_at DESC"

    sql += " LIMIT 10"

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params)
    articles = cursor.fetchall()
    cursor.close()

    return jsonify({
        "status": "success",
        "articles": articles
    })

@user_article_bp.route("/categories", methods=["GET"])
def get_categories():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM categories WHERE hidden = 0 OR hidden IS NULL")
    categories = [row["name"] for row in cursor.fetchall()]
    cursor.close()
    return jsonify({"status": "success", "categories": categories})