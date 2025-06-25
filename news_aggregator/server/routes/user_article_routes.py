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

    if category == "all":
        cursor.execute(
            """
            SELECT n.id, n.title, n.url, c.name as category
            FROM news_articles n
            LEFT JOIN categories c ON n.category_id = c.id
            WHERE DATE(n.published_at) BETWEEN %s AND %s
              AND n.is_hidden = 0
            ORDER BY n.published_at DESC
            LIMIT 20
        """,
            (start, end),
        )
    else:
        cursor.execute(
            """
            SELECT n.id, n.title, n.url, c.name as category
            FROM news_articles n
            LEFT JOIN categories c ON n.category_id = c.id
            WHERE DATE(n.published_at) BETWEEN %s AND %s
              AND c.name = %s
              AND n.is_hidden = 0
            ORDER BY n.published_at DESC
            LIMIT 20
        """,
            (start, end, category),
        )

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
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, title, url, content, source, published_at, category_id
        FROM news_articles
        WHERE title LIKE %s OR content LIKE %s
        ORDER BY published_at DESC
        LIMIT 10
    """,
        (f"%{query}%", f"%{query}%"),
    )
    results = cursor.fetchall()

    for row in results:
        cursor.execute(
            "SELECT name FROM categories WHERE id = %s", (row["category_id"],)
        )
        category = cursor.fetchone()
        row["category"] = category["name"] if category else "general"

    cursor.close()
    return jsonify({"status": "success", "articles": results})
