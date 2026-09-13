import requests
from bs4 import BeautifulSoup


URL = "https://warthunder.com/ru/news"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}


def main():
    print(f"Получаем: {URL}")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    print(f"HTTP статус: {response.status_code}")
    print(f"Размер страницы: {len(response.text)} символов")

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Ищем ВСЕ ссылки, в которых есть /news/
    links = soup.find_all("a", href=True)

    print(f"Всего ссылок на странице: {len(links)}")
    print()
    print("Ссылки, связанные с news:")
    print("=" * 100)

    count = 0

    for a in links:

        href = a.get("href", "")

        if "/news" not in href:
            continue

        text = a.get_text(" ", strip=True)

        print(f"TEXT: {text[:150]}")
        print(f"HREF: {href}")
        print("-" * 100)

        count += 1

        if count >= 50:
            break

    print()
    print(f"Показано ссылок: {count}")


if __name__ == "__main__":
    main()