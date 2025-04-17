import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

if os.getenv("GITHUB_ACTIONS") != "true":
    load_dotenv()

EVENT_CITY = {
    122: "Abilene, TX",
    123: "Houston, TX",
    124: "San Antonio, TX"
}

SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def process_page(event_num):
    response = requests.get(f"https://tmomvolunteer.org/event/{event_num}")
    soup = BeautifulSoup(response.content, 'html.parser')
    unavailable_msg = soup.find("div", id="registration")
    if unavailable_msg and "Registration for this event is currently unavailable" in unavailable_msg.text:
        return False
    return True

def send_email_alert(event_num):
    event_url = f"https://tmomvolunteer.org/event/{event_num}"
    city = EVENT_CITY[event_num]
    
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = f"🦷 TMOM Alert: Sign-Ups Open in {city}!"

    text_part = f"Sign-ups for TMOM in {city} are now OPEN!\nRegister here: {event_url}"
    
    html_part = f"""
    <html>
      <head>
        <style>
          a.tmom-link {{
            color: #3b82f6;
            text-decoration: none;
            font-size: 18px;
          }}
          a.tmom-link:hover {{
            color: #1e3a8a;
          }}
        </style>
      </head>
      <body style="font-family: Arial, sans-serif; background-color: #f0f4f8; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; padding: 20px;">
          <h2 style="color: #2563eb;">🦷 TMOM Volunteer Opportunity</h2>
          <p style="font-size: 16px; color: #374151;">
            Great news! Volunteer sign-ups for the upcoming TMOM event in <strong>{city}</strong> are now available.
          </p>
          <p style="font-size: 16px; margin-bottom: 20px;">
            Click the link below to sign up or view more details:
          </p>
          <p>
            <a href="{event_url}" class="tmom-link">{event_url}</a>
          </p>
          <p style="font-size: 12px; color: #6b7280; text-align: center; margin-top: 30px;">
            This is an automated alert from your TMOM sign-up tracker.
          </p>
        </div>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(text_part, "plain"))
    msg.attach(MIMEText(html_part, "html"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print(f"📧 Email sent: Sign-ups available for TMOM in {city}")
    except Exception as e:
        print("❌ Failed to send email:", e)

if __name__ == "__main__":
    try:
        for event_num in EVENT_CITY:
            city = EVENT_CITY[event_num]
            if process_page(event_num):
                print(f"🔍 Checking {city}...")
                send_email_alert(event_num)
            else:
                print(f"🛑 Sign-ups not available for {city}")

    except Exception as e:
        print("Error in main loop:", e)
