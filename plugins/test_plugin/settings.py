import os
from dotenv import load_dotenv

# Load local .env file if it exists
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Settings:
    """
    Settings for the Test_plugin plugin.
    Values are loaded from environment variables.
    """
    api_key: str = ""
    enabled: bool = True

    def __init__(self):
        self.api_key = os.getenv("TEST_PLUGIN_API_KEY", "")
        self.enabled = os.getenv("TEST_PLUGIN_ENABLED", "true").lower() == "true"


settings = Settings()
