import requests, os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')


def get_latest_news(query="Ukraine", language="uk", limit=10) -> list:

    """
    Returns the list of dictionaries: title, description, url, image, date.
    """

    url = (
        "https://newsapi.org/v2/everything"
        f"?q={query}"
        f"&language={language}"
        f"&sortBy=publishedAt"
        f"&pageSize={limit}"
        f"&apiKey={NEWS_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    # Перевірка на помилку
    if data.get("status") != "ok":
        return {"error": data.get("message", "Unknown error")}

    articles = []

    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title"),
            "description": item.get("description"),
            "url": item.get("url"),
            "image": item.get("urlToImage"),
            "published": item.get("publishedAt")
        })

    return articles


if __name__ == "__main__":
    news_list = get_latest_news(limit=5)

    for n in news_list:
        print("🔹", n["title"])
        print("   📅", n["published"])
        print("   🔗", n["url"])
        print()
