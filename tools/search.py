from duckduckgo_search import DDGS


def search_tool(query):

    results = list(
        DDGS().text(
            query,
            max_results=5
        )
    )

    return results