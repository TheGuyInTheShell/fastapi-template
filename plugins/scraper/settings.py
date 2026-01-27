import os
from dotenv import load_dotenv

load_dotenv( os.path.join(os.path.dirname(__file__), ".env") )

"""
create settings.py file in the same directory as this file of the plugin
with the following content:

EMAIL_LINKEDIN=your_email
PASSWORD_LINKEDIN=your_password

"""

class Settings:
    email_linkedin: str = ""
    password_linkedin: str = ""

    def __init__(self):
        self.email_linkedin = os.getenv("EMAIL_LINKEDIN", "")
        self.password_linkedin = os.getenv("PASSWORD_LINKEDIN", "")


settings = Settings()