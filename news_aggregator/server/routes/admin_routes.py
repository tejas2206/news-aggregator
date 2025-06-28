from flask import Blueprint, request, jsonify
from server.db.database import get_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/servers/status", methods=["GET"])
def view_server_status():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, status, last_accessed FROM external_servers")
    servers = cursor.fetchall()
    cursor.close()
    return jsonify({"status": "success", "servers": servers})


@admin_bp.route("/servers/details", methods=["GET"])
def view_server_details():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, api_key FROM external_servers")
    servers = cursor.fetchall()
    cursor.close()
    return jsonify({"status": "success", "servers": servers})


@admin_bp.route("/servers/update", methods=["POST"])
def update_server_api_key():
    data = request.get_json()
    server_id = data.get("server_id")
    new_key = data.get("api_key")

    if not server_id or not new_key:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE external_servers SET api_key = %s WHERE id = %s", (new_key, server_id)
    )
    conn.commit()
    cursor.close()

    return jsonify({"status": "success", "message": "API key updated successfully."})


@admin_bp.route("/categories/add", methods=["POST"])
def add_category():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"status": "error", "message": "Missing category name"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()

    return jsonify({"status": "success", "message": f"Category '{name}' added."})


@admin_bp.route("/reports", methods=["GET"])
def view_reported_articles():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            MAX(na.id) AS id,
            MAX(na.title) AS title,
            MAX(na.url) AS url,
            MAX(na.content) AS content,
            COUNT(ar.id) AS report_count
        FROM article_reports ar
        JOIN news_articles na ON ar.article_id = na.id
        WHERE na.is_hidden = 1 or na.is_hidden = 0
        GROUP BY ar.article_id
        ORDER BY report_count DESC
    """)
    reports = cursor.fetchall()
    cursor.close()
    return jsonify({"status": "success", "reports": reports})


@admin_bp.route("/articles/hide", methods=["POST"])
def admin_hide_article():
    data = request.get_json()
    article_id = data.get("article_id")
    hide = data.get("hide", True)  # pass hide: true/false

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE news_articles SET is_hidden = %s WHERE id = %s", (hide, article_id))
    conn.commit()
    cursor.close()
    status = "hidden" if hide else "unhidden"
    return jsonify({"status": "success", "message": f"Article {article_id} {status} successfully."})

@admin_bp.route("/categories/toggle", methods=["POST"])
def toggle_category_visibility():
    data = request.get_json()
    category_name = data.get("category")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE categories
        SET hidden = NOT hidden
        WHERE name = %s
    """, (category_name,))
    
    conn.commit()
    cursor.close()

    return jsonify({"status": "success", "message": f"Visibility toggled for category '{category_name}'."})
