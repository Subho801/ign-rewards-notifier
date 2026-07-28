import requests
from bs4 import BeautifulSoup

URL = "https://www.ign.com/rewards"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

buttons = soup.select("button.reward-button")

print(f"Found {len(buttons)} rewards\n")

for i, button in enumerate(buttons, start=1):
    title = " ".join(button.stripped_strings)

    link = None

    parent = button.parent
    while parent:
        if parent.name == "a":
            link = parent.get("href")
            break
        parent = parent.parent

    print("=" * 70)
    print("TITLE:")
    print(title)

    print("\nLINK:")
    print(link)
