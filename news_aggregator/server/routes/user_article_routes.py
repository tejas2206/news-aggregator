from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from server.services.user_article_service import UserArticleService

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
