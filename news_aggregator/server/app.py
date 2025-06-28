from flask import Flask
from server.routes.auth_routes import auth_bp
from server.routes.user_notification_routes import user_notification_bp
from server.routes.user_article_routes import user_article_bp
from server.routes.admin_routes import admin_bp
from server.routes.user_feedback_routes import user_feedback_bp
from server.routes.article_reports_routes import article_report_bp
from server.db.database import init_db
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret")

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_article_bp, url_prefix="/user")
    app.register_blueprint(user_notification_bp, url_prefix="/user")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_feedback_bp, url_prefix="/user")
    app.register_blueprint(article_report_bp, url_prefix="/user")

    init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} | {rule.rule} [{','.join(rule.methods)}]")
    app.run(debug=True)
