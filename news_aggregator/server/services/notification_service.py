import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage
from server.db.database import get_db
from pathlib import Path
from datetime import datetime

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


class NotificationService:
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASSWORD")

    def notify_users_about_articles(self, articles):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        cursor.close()

        for user in users:
            matching_articles = [
                article
                for article in articles
                if self._article_matches_user_preferences(user["id"], article, conn)
            ]
            if matching_articles:
                self._send_email(user["id"], user["email"], matching_articles)

    def _article_matches_user_preferences(self, user_id, article, conn):
        category_match = False
        keyword_match = False

        try:
            cursor1 = conn.cursor(buffered=True)
            cursor1.execute(
                "SELECT 1 FROM notifications WHERE user_id = %s AND category = %s AND enabled = 1",
                (user_id, article["category"]),
            )
            if cursor1.fetchone():
                category_match = True
            cursor1.close()
        except Exception as e:
            print(f"[ERROR] category check failed: {e}")

        if category_match:
            return True

        try:
            cursor2 = conn.cursor(buffered=True)
            cursor2.execute(
                "SELECT keyword FROM user_keywords WHERE user_id = %s AND enabled = 1",
                (user_id,),
            )
            keywords = cursor2.fetchall()
            cursor2.close()

            for row in keywords:
                keyword = row[0]
                if keyword.lower() in (article["title"] or "").lower():
                    keyword_match = True
                    break
        except Exception as e:
            print(f"[ERROR] keyword match check failed: {e}")

        return keyword_match

    # def _send_email(self, recipient, articles):
    #     if not self.email_user or not self.email_pass:
    #         print("Email not configured in .env")
    #         return

    #     msg = EmailMessage()
    #     msg["Subject"] = "News Alert - Matching Articles"
    #     msg["From"] = self.email_user
    #     msg["To"] = recipient

    #     body = "Hello!\nHere are some articles matching your preferences:\n\n"
    #     for article in articles:
    #         body += f"{article['title']} ({article['url']})\n"

    #     body += "\nRegards,\nNews Aggregator Team"
    #     msg.set_content(body)

    #     try:
    #         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    #             smtp.login(self.email_user, self.email_pass)
    #             smtp.send_message(msg)
    #             print(f"Email sent to {recipient}")

    #     except Exception as e:
    #         print(f"Failed to send email to {recipient}: {e}")

    def _send_email(self, user_id, recipient, articles):
        if not self.email_user or not self.email_pass:
            print("Email not configured in .env")
            return

        msg = EmailMessage()
        msg["Subject"] = "News Alert - Matching Articles"
        msg["From"] = self.email_user
        msg["To"] = recipient

        body = "Hello!\nHere are some articles matching your preferences:\n\n"
        for article in articles:
            body += f"{article['title']} ({article['url']})\n"

        body += "\nRegards,\nNews Aggregator Team"
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.email_user, self.email_pass)
                smtp.send_message(msg)
                print(f"[INFO] Email sent to {recipient}")

            conn = get_db()
            cursor = conn.cursor()
            for article in articles:
                cursor.execute(
                    """
                    INSERT INTO sent_notifications (user_id, article_id, sent_at)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, article["id"], datetime.now())
                )
            conn.commit()
            cursor.close()

        except Exception as e:
            print(f"[ERROR] Failed to send email to {recipient}: {e}")


    def notify_admin_about_report(self, article_id, reported_by):
        if not self.email_user or not self.email_pass:
            print("Email not configured.")
            return

        msg = EmailMessage()
        msg["Subject"] = f"Article Reported - ID {article_id}"
        msg["From"] = self.email_user
        msg["To"] = os.getenv("ADMIN_EMAIL", self.email_user)

        body = f"""
    Hello Admin,

    An article has been reported by user: {reported_by}

    Reported Article ID: {article_id}
    Please review and take necessary action.

    Regards,
    News Aggregator Team
    """
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.email_user, self.email_pass)
                smtp.send_message(msg)
                print(f"[INFO] Admin notified about report on article {article_id}")
        except Exception as e:
            print(f"[ERROR] Failed to notify admin: {e}")
