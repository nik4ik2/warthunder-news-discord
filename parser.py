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

    # Ищем все карточки новостей
    for widget in soup.select(".showcase__item.widget"):

        link = widget.select_one("a.widget__link[href]")

        if not link:
            continue

        href = link["href"]

        # Только настоящие новости
        if not href.startswith("/ru/news/"):
            continue

        if "/page/" in href or "?" in href:
            continue

        url = urljoin(BASE_URL, href)

        if url in seen:
            continue

        seen.add(url)

        # ID новости
        slug = href.rstrip("/").split("/")[-1]
        news_id = slug.split("-")[0]

        if not news_id.isdigit():
            continue

        # Заголовок
        title_element = widget.select_one(".widget__title")
        title = (
            clean_text(title_element.get_text(" ", strip=True))
            if title_element
            else ""
        )

        # Описание
        comment_element = widget.select_one(".widget__comment")
        description = (
            clean_text(comment_element.get_text(" ", strip=True))
            if comment_element
            else ""
        )

        # Дата
        date_element = widget.select_one(".widget-meta__item")
        date = (
            clean_text(date_element.get_text(" ", strip=True))
            if date_element
            else ""
        )

        # Картинка
        image_element = widget.select_one(".widget__poster-media")

        image = ""

        if image_element:

            image = (
                image_element.get("data-src")
                or image_element.get("src")
                or ""
            )

            if image.startswith("//"):
                image = "https:" + image

            elif image.startswith("/"):
                image = urljoin(BASE_URL, image)

        news.append({
            "id": news_id,
            "title": title,
            "description": description,
            "date": date,
            "image": image,
            "url": url
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

        print(f"ID:          {item['id']}")
        print(f"TITLE:       {item['title']}")
        print(f"DESCRIPTION: {item['description']}")
        print(f"DATE:        {item['date']}")
        print(f"IMAGE:       {item['image']}")
        print(f"URL:         {item['url']}")

    print()
    print("Готово.")


if __name__ == "__main__":
    main()