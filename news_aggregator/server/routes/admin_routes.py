from flask import Blueprint, request, jsonify
import logging
from server.services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__)
admin_service = AdminService(logger=logging.getLogger("admin_service"))


@admin_bp.route("/servers/status", methods=["GET"])
def view_server_status():
    servers = admin_service.get_server_status()
    return jsonify({"status": "success", "servers": servers})


@admin_bp.route("/servers/details", methods=["GET"])
def view_server_details():
    servers = admin_service.get_server_details()
    return jsonify({"status": "success", "servers": servers})


@admin_bp.route("/servers/update", methods=["POST"])
def update_server_api_key():
    data = request.get_json()
    server_id = data.get("server_id")
    new_key = data.get("api_key")
    if not server_id or not new_key:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    success = admin_service.update_server_api_key(server_id, new_key)
    if success:
        return jsonify(
            {"status": "success", "message": "API key updated successfully."}
        )
    else:
        return jsonify({"status": "error", "message": "Failed to update API key."}), 500


@admin_bp.route("/categories/add", methods=["POST"])
def add_category():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"status": "error", "message": "Missing category name"}), 400
    success = admin_service.add_category(name)
    if success:
        return jsonify({"status": "success", "message": f"Category '{name}' added."})
    else:
        return jsonify({"status": "error", "message": "Failed to add category."}), 500


@admin_bp.route("/reports", methods=["GET"])
def view_reported_articles():
    reports = admin_service.get_reported_articles()
    return jsonify({"status": "success", "reports": reports})


@admin_bp.route("/articles/hide", methods=["POST"])
def admin_hide_article():
    data = request.get_json()
    article_id = data.get("article_id")
    hide = data.get("hide", True)
    success = admin_service.hide_article(article_id, hide)
    status = "hidden" if hide else "unhidden"
    if success:
        return jsonify(
            {
                "status": "success",
                "message": f"Article {article_id} {status} successfully.",
            }
        )
    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to update article {article_id}.",
                }
            ),
            500,
        )


@admin_bp.route("/categories/toggle", methods=["POST"])
def toggle_category_visibility():
    data = request.get_json()
    category_name = data.get("category")
    success = admin_service.toggle_category_visibility(category_name)
    if success:
        return jsonify(
            {
                "status": "success",
                "message": f"Visibility toggled for category '{category_name}'.",
            }
        )
    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to toggle category '{category_name}'.",
                }
            ),
            500,
        )


@admin_bp.route("/blocked_keywords", methods=["POST"])
def add_blocked_keyword():
    data = request.get_json()
    keyword = data.get("keyword")
    success = admin_service.add_blocked_keyword(keyword)
    if success:
        return jsonify(
            {"status": "success", "message": f"Keyword '{keyword}' blocked."}
        )
    else:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to block keyword '{keyword}'."}
            ),
            500,
        )


@admin_bp.route("/blocked_keywords", methods=["DELETE"])
def delete_blocked_keyword():
    keyword = request.args.get("keyword")
    success = admin_service.remove_blocked_keyword(keyword)
    if success:
        return jsonify(
            {"status": "success", "message": f"Keyword '{keyword}' unblocked."}
        )
    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to unblock keyword '{keyword}'.",
                }
            ),
            500,
        )


@admin_bp.route("/blocked_keywords", methods=["GET"])
def list_blocked_keywords():
    keywords = admin_service.get_blocked_keywords()
    return jsonify({"status": "success", "keywords": keywords})
