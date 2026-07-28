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

print("Downloading IGN Rewards page...")

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

print(f"Status Code: {response.status_code}")

soup = BeautifulSoup(response.text, "lxml")

cards = soup.select('[data-cy="rewardCard"]')

print(f"\nFound {len(cards)} reward cards\n")

for i, card in enumerate(cards, start=1):

    title = card.select_one('[data-cy="cardTitle"]')
    image = card.select_one('[data-cy="rewardImg"] img')
    end_date = card.select_one('[data-cy="endDate"]')
    availability = card.select_one('[data-cy="availability"]')

    print("=" * 70)
    print(f"Reward #{i}")

    print("\nTITLE:")
    print(title.get_text(strip=True) if title else "None")

    print("\nIMAGE:")
    print(image.get("src") if image else "None")

    print("\nEND DATE:")
    print(end_date.get_text(strip=True) if end_date else "None")

    print("\nAVAILABILITY:")
    print(availability.get_text(strip=True) if availability else "None")
