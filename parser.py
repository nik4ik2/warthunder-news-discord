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


response = requests.get(
    NEWS_URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


# Ищем конкретную свежую новость
target = None

for a in soup.find_all("a", href=True):
    if "/ru/news/18006-" in a["href"]:
        target = a
        break


if target is None:
    print("Новость 18006 не найдена!")
    exit()


print("=" * 100)
print("НАЙДЕННАЯ ССЫЛКА")
print("=" * 100)

print(target)

print()
print("=" * 100)
print("HTML РОДИТЕЛЯ")
print("=" * 100)

parent = target.parent

print(parent.prettify()[:10000])

print()
print("=" * 100)
print("HTML РОДИТЕЛЯ РОДИТЕЛЯ")
print("=" * 100)

parent2 = parent.parent

print(parent2.prettify()[:15000])

print()
print("=" * 100)
print("ЗАГОЛОВКИ В БЛОКЕ")
print("=" * 100)

for tag in parent2.find_all(["h1", "h2", "h3", "h4", "h5"]):
    print("TAG:", tag.name)
    print("TEXT:", tag.get_text(" ", strip=True))
    print()

print()
print("=" * 100)
print("КАРТИНКИ В БЛОКЕ")
print("=" * 100)

for img in parent2.find_all("img"):
    print("SRC:", img.get("src"))
    print("DATA-SRC:", img.get("data-src"))
    print("ALT:", img.get("alt"))
    print()

print()
print("=" * 100)
print("ТЕКСТ БЛОКА")
print("=" * 100)

print(parent2.get_text("\n", strip=True)[:10000])

print()
print("=" * 100)
print("ГОТОВО")
print("=" * 100)