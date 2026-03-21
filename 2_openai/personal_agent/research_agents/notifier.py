import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.schemas import Report


# -----------------------------
# Format Report for Email
# -----------------------------
def format_report_html(report: Report) -> str:
    insights_html = "".join(f"<li>{insight}</li>" for insight in report.key_insights)
    risks_html = "".join(f"<li>{risk}</li>" for risk in report.risks)

    html = f"""
    <html>
        <body>
            <h1>{report.title}</h1>

            <h2>Key Insights</h2>
            <ul>{insights_html}</ul>

            <h2>Analysis</h2>
            <p>{report.analysis}</p>

            <h2>Risks / Counterpoints</h2>
            <ul>{risks_html}</ul>

            <h2>Conclusion</h2>
            <p>{report.conclusion}</p>
        </body>
    </html>
    """

    return html


# -----------------------------
# 📧 Send Email (SendGrid)
# -----------------------------
def send_email(report: Report):
    html_content = format_report_html(report)

    message = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        to_emails=os.getenv("TO_EMAIL"),
        subject=report.title,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Email failed: {e}")


# -----------------------------
# Send Push (Pushover)
# -----------------------------
def send_push_notification(report: Report):
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "title": "AI Research Complete",
                "message": report.title,
            }
        )
        print("✅ Push notification sent")
    except Exception as e:
        print(f"❌ Push failed: {e}")