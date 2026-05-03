"""Search tools for evidence gathering."""

from langchain_community.tools import DuckDuckGoSearchResults


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for evidence on a topic."""
    try:
        tool = DuckDuckGoSearchResults(num_results=max_results)
        return tool.invoke(query)
    except Exception as e:
        return f"Search failed: {e}"
