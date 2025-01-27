from authlib.integrations.starlette_client import OAuth
from core.config import settings
import smtplib
from email.mime.text import MIMEText

class OAuthGoogle:
    oauth = OAuth()
    name: str = "google"
    
    CLIENT_ID: str = settings.GOOGLE_CLIENT_ID
    CLIENT_SECRET: str = settings.GOOGLE_CLIENT_SECRET
    SECRET_KEY: str = settings.SECRET_KEY
    REDIRECT_URL: str = settings.REDIRECT_URL

    @classmethod
    def register(cls):
        cls.oauth.register(
            name=cls.name,
            client_id=cls.CLIENT_ID,
            client_secret=cls.CLIENT_SECRET,
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            access_token_url="https://accounts.google.com/o/oauth2/token",
            authorize_state=cls.SECRET_KEY,
            redirect_uri=cls.REDIRECT_URL,
            jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
            client_kwargs={"scope": "openid profile email"},
        )

class Gmail:
    sender = settings.EMAIL_NAME
    password = settings.EMAIL_PASSWORD

    def send_msg(cls, subject: str, body: str, recipient: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = cls.sender
        msg["To"] = recipient
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(cls.sender, cls.password)
            smtp_server.sendmail(cls.sender, recipient, msg.as_string())
        print("Message sent")