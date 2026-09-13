import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin, quote

import requests
from bs4 import BeautifulSoup


NEWS_URL = "https://warthunder.com/ru/news"
BASE_URL = "https://warthunder.com"

STATE_FILE = Path("data/sent_news.json")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

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

    for widget in soup.select(".showcase__item.widget"):

        link = widget.select_one("a.widget__link[href]")

        if not link:
            continue

        href = link["href"]

        if not href.startswith("/ru/news/"):
            continue

        if "/page/" in href or "?" in href:
            continue

        url = urljoin(BASE_URL, href)

        if url in seen:
            continue

        seen.add(url)

        slug = href.rstrip("/").split("/")[-1]
        news_id = slug.split("-")[0]

        if not news_id.isdigit():
            continue

        title_element = widget.select_one(".widget__title")
        title = (
            clean_text(title_element.get_text(" ", strip=True))
            if title_element
            else ""
        )

        comment_element = widget.select_one(".widget__comment")
        description = (
            clean_text(comment_element.get_text(" ", strip=True))
            if comment_element
            else ""
        )

        date_element = widget.select_one(".widget-meta__item")
        date = (
            clean_text(date_element.get_text(" ", strip=True))
            if date_element
            else ""
        )

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

            # Кодируем пробелы и другие символы в URL
            image = quote(image, safe=":/?&=#")

        news.append({
            "id": news_id,
            "title": title,
            "description": description,
            "date": date,
            "image": image,
            "url": url
        })

    return news


def load_sent():

    if not STATE_FILE.exists():
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return set(str(x) for x in data)

    except Exception as e:
        print(f"Ошибка чтения состояния: {e}")
        return set()


def save_sent(sent):

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            sorted(sent, key=int),
            f,
            ensure_ascii=False,
            indent=2
        )


def send_to_discord(item):

    if not WEBHOOK_URL:
        raise RuntimeError(
            "Не найден секрет DISCORD_WEBHOOK_URL"
        )

    description = item["description"]

    if len(description) > 4096:
        description = description[:4093] + "..."

    embed = {
        "author": {
            "name": "War Thunder | Официальные новости"
        },
        "title": item["title"],
        "description": description,
        "color": 0xF50000,
        "url": item["url"],
        "footer": {
            "text": "War Thunder • Новости"
        }
    }

    if item["image"]:
        embed["image"] = {
            "url": item["image"]
        }

    payload = {
        "username": "War Thunder News",
        "allowed_mentions": {
            "parse": []
        },
        "embeds": [embed]
    }

    while True:

        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=30
        )

        if response.status_code == 204:
            print(
                f"✓ Отправлено: "
                f"{item['id']} — {item['title']}"
            )
            return

        if response.status_code == 429:

            try:
                retry_after = response.json().get(
                    "retry_after",
                    1
                )
            except Exception:
                retry_after = 1

            print(
                f"Discord ограничил отправку. "
                f"Ждём {retry_after} сек..."
            )

            time.sleep(float(retry_after) + 0.2)
            continue

        raise RuntimeError(
            f"Discord вернул {response.status_code}: "
            f"{response.text}"
        )


def main():

    print("Получаем новости War Thunder...")
    print()

    news = get_news()

    print(f"Найдено новостей: {len(news)}")

    sent = load_sent()

    print(f"Уже отправлено: {len(sent)}")

    new_news = [
        item for item in news
        if item["id"] not in sent
    ]

    print(f"Новых новостей: {len(new_news)}")
    print()

    if not new_news:
        print("Новых новостей нет.")
        return

    # Старые новости отправляем первыми
    new_news.sort(key=lambda x: int(x["id"]))

    for item in new_news:

        try:
            send_to_discord(item)
            sent.add(item["id"])

            time.sleep(1)

        except Exception as e:

            print(
                f"✗ Ошибка отправки "
                f"{item['id']}: {e}"
            )

            break

    save_sent(sent)

    print()
    print("Готово.")


if __name__ == "__main__":
    main()