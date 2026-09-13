import requests
from bs4 import BeautifulSoup


URL = "https://warthunder.com/ru/news"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
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

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/ru/news/" not in href:
            continue

        title = a.get_text(" ", strip=True)

        if not title:
            continue

        links.append((title, href))

    print()
    print(f"Найдено ссылок на новости: {len(links)}")
    print()

    for title, href in links[:20]:
        print("=" * 80)
        print(f"TITLE: {title}")
        print(f"URL:   {href}")


if __name__ == "__main__":
    main()