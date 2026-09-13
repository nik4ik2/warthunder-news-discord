import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


NEWS_URL = "https://warthunder.com/ru/news"
BASE_URL = "https://warthunder.com"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}


def clean_text(text):
    return " ".join(text.split())


def get_news():

    response = requests.get(
        NEWS_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    news = []
    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        # Нас интересуют только реальные статьи.
        # Фильтры и пагинация сюда не попадут.
        if not href.startswith("/ru/news/"):
            continue

        # Исключаем пагинацию
        if "/page/" in href:
            continue

        # Исключаем URL с параметрами
        if "?" in href:
            continue

        url = urljoin(BASE_URL, href)

        # Уже встречали эту новость
        if url in seen:
            continue

        seen.add(url)

        # ID новости
        parts = href.split("/")

        if len(parts) < 4:
            continue

        slug = parts[3]

        try:
            news_id = slug.split("-")[0]

            if not news_id.isdigit():
                continue

        except Exception:
            continue

        # Пока title берём из атрибутов/текста ссылки.
        title = clean_text(a.get_text(" ", strip=True))

        news.append({
            "id": news_id,
            "url": url,
            "title": title,
        })

    return news


def main():

    print("Получаем новости War Thunder...")
    print()

    news = get_news()

    print(f"Найдено новостей: {len(news)}")
    print()

    for item in news:

        print("=" * 100)

        print(f"ID:    {item['id']}")
        print(f"TITLE: {item['title']}")
        print(f"URL:   {item['url']}")

    print()
    print("Готово.")


if __name__ == "__main__":
    main()