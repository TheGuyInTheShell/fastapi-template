from core.config.globals import settings

class Config:
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
    MODEL_NAME = settings.IA_MODEL_NAME
    TEMPERATURE = 0.7

config = Config()
