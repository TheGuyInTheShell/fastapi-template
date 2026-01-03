from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..core.llm import llm

WRITER_PROMPT = """You are a professional writer. 
Your goal is to take the research findings and transform them into a cohesive, engaging, and well-structured document.
Focus on clarity, tone, and flow."""

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", WRITER_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

writer_agent = writer_prompt | llm
