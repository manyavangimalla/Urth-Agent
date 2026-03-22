import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "")
EMAIL_TO   = os.getenv("ALERT_EMAIL_TO", "")
EMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD", "")


def should_alert(risk_level: str) -> bool:
    """Only send alerts for HIGH or EXTREME risk."""
    return risk_level.upper() in ("HIGH", "EXTREME")


def build_email(region: str, risk_level: str, report: str, fire_data: str, air_data: str) -> MIMEMultipart:
    """Build the alert email with HTML formatting."""

    risk_color = {
        "HIGH":    "#e67e22",
        "EXTREME": "#e74c3c",
    }.get(risk_level.upper(), "#e74c3c")

    # Truncate report for email
    report_preview = report[:800] + "..." if len(report) > 800 else report
    fire_preview   = fire_data[:400] + "..." if len(fire_data) > 400 else fire_data

    html = f"""
    <html><body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

        <!-- Header -->
        <div style="background: {risk_color}; padding: 24px; text-align: center;">
          <h1 style="color: white; margin: 0; font-size: 22px;">
            ⚠️ EARTH AGENT ALERT
          </h1>
          <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0; font-size: 14px;">
            Environmental Risk Level: <strong>{risk_level}</strong>
          </p>
        </div>

        <!-- Body -->
        <div style="padding: 24px;">
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
              <td style="padding: 8px 12px; background: #f8f8f8; border-radius: 4px; font-weight: bold; width: 120px;">Region</td>
              <td style="padding: 8px 12px;">{region}</td>
            </tr>
            <tr>
              <td style="padding: 8px 12px; background: #f8f8f8; border-radius: 4px; font-weight: bold;">Risk Level</td>
              <td style="padding: 8px 12px; color: {risk_color}; font-weight: bold;">{risk_level}</td>
            </tr>
            <tr>
              <td style="padding: 8px 12px; background: #f8f8f8; border-radius: 4px; font-weight: bold;">Generated</td>
              <td style="padding: 8px 12px;">{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</td>
            </tr>
          </table>

          <h3 style="color: #333; border-bottom: 2px solid {risk_color}; padding-bottom: 8px;">
            🔥 Fire Data (NASA FIRMS)
          </h3>
          <pre style="background: #f8f8f8; padding: 12px; border-radius: 6px; font-size: 12px; white-space: pre-wrap; color: #444;">{fire_preview}</pre>

          <h3 style="color: #333; border-bottom: 2px solid {risk_color}; padding-bottom: 8px;">
            📊 Assessment Summary
          </h3>
          <pre style="background: #f8f8f8; padding: 12px; border-radius: 6px; font-size: 12px; white-space: pre-wrap; color: #444;">{report_preview}</pre>

          <div style="margin-top: 24px; padding: 16px; background: #fff3cd; border-radius: 8px; border-left: 4px solid {risk_color};">
            <strong>⚡ Automated Alert</strong><br>
            <small style="color: #666;">
              This alert was generated automatically by the Earth Intelligence Agent
              using LangGraph pipeline + MCP server tools (NASA FIRMS, OpenAQ, Open-Meteo).
              Risk threshold: HIGH or EXTREME only.
            </small>
          </div>
        </div>

        <!-- Footer -->
        <div style="background: #f0f0f0; padding: 16px; text-align: center; font-size: 11px; color: #999;">
          Earth Intelligence Agent · LangGraph + MCP · Environmental AI
        </div>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[EARTH AGENT] {risk_level} Risk Alert — {region}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    return msg


def send_alert(region: str, risk_level: str, report: str,
               fire_data: str = "", air_data: str = "") -> dict:
    """
    Send an alert email if risk is HIGH or EXTREME.
    Returns a dict with success status and message.
    """
    if not should_alert(risk_level):
        return {
            "sent": False,
            "reason": f"Risk level {risk_level} is below alert threshold (need HIGH or EXTREME)"
        }

    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_PASS]):
        print("[Alert] Email credentials not configured — skipping send")
        return {
            "sent": False,
            "reason": "Email credentials not configured in .env"
        }

    try:
        msg = build_email(region, risk_level, report, fire_data, air_data)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        print(f"[Alert] Email sent to {EMAIL_TO} — {risk_level} risk in {region}")
        return {
            "sent": True,
            "to": EMAIL_TO,
            "subject": msg["Subject"],
        }

    except Exception as e:
        print(f"[Alert] Email failed: {e}")
        return {"sent": False, "reason": str(e)}


if __name__ == "__main__":
    # Test the alert system
    print("Testing alert system...")
    result = send_alert(
        region="Northern California",
        risk_level="HIGH",
        report="Test report — HIGH wildfire risk detected.",
        fire_data="34 active hotspots. Max FRP: 187 MW.",
        air_data="PM2.5: 42.1 µg/m³ — Unhealthy for Sensitive Groups."
    )
    print(f"Result: {result}")
