from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No results found on the web."
            
            formatted_results = []
            for r in results:
                formatted_results.append(f"Title: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}")
                
            return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error searching the web: {str(e)}"
