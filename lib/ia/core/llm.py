from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .config import config

def get_llm(provider="openai"):
    if provider == "openai":
        return ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            api_key=config.ANTHROPIC_API_KEY,
            model="claude-3-opus-20240229",
            temperature=config.TEMPERATURE
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# Default LLM instance
llm = get_llm()
