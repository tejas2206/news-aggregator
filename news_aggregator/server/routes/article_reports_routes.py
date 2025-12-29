from flask import Blueprint, request, jsonify
import logging
from server.services.article_report_service import ArticleReportService

article_report_bp = Blueprint("article_report", __name__)
article_report_service = ArticleReportService(
    logger=logging.getLogger("article_report_service")
)


@article_report_bp.route("/articles/report", methods=["POST"])
def report_article():
    data = request.get_json()
    email = data.get("email")
    article_id = data.get("article_id")
    success, message = article_report_service.report_article(email, article_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 400
