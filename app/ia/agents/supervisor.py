from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..core.llm import llm

class RouteResponse(BaseModel):
    next_step: Literal["Researcher", "Writer", "Finish"] = Field(
        ..., 
        description="The next agent to call or 'Finish' if the task is complete."
    )

SUPERVISOR_PROMPT = """You are a supervisor tasked with managing a conversation between the following workers: Researcher, Writer.
Given the following user request, respond with the worker to act next. 
Each worker will perform a task and respond with their results and status.
When finished, respond with FINISH."""

supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", SUPERVISOR_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

supervisor_agent = supervisor_prompt | llm.with_structured_output(RouteResponse)
