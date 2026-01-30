import requests

def search_google(query, api_key, cse_id, num_results=5):
    """Search Google using Custom Search API and return top results (title, link, snippet)."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return results

# Example usage (replace with your API key and CSE ID):
# api_key = "YOUR_GOOGLE_API_KEY"
# cse_id = "YOUR_CUSTOM_SEARCH_ENGINE_ID"
# print(search_google("AI in healthcare", api_key, cse_id))
