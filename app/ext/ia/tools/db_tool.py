from typing import Any
from langchain_core.tools import tool

@tool
def db_tool(query: str) -> str:
    """
    Executes a read-only SQL query against the database and returns the results.
    Use this for fetching information from the system.
    """
    # This is a placeholder for actual DB interaction logic
    # In a real scenario, you'd use SQLAlchemy or a similar ORM here.
    return f"Executed query: {query}. Result: Sample data from database."
