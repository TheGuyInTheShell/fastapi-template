import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-ant-...")
    MODEL_NAME = os.getenv("IA_MODEL_NAME", "gpt-4-turbo-preview")
    TEMPERATURE = 0.7

config = Config()
