from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..core.llm import llm
from ..tools.search_tool import search_tool

RESEARCHER_PROMPT = """You are a world-class researcher. 
Your goal is to find accurate and relevant information on the given topic.
Use the search tool to find facts and details."""

researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", RESEARCHER_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

# Researcher "Chain" or "Agent" partial implementation
researcher_agent = researcher_prompt | llm.bind_tools([search_tool])
