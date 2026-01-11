from langchain_community.tools.tavily_search import TavilySearchResults

def get_search_tool():
    """
    Returns a search tool instance.
    Requires TAVILY_API_KEY in environment.
    """
    return TavilySearchResults(max_results=3)

search_tool = get_search_tool()
