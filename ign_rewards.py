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

print("\nPage title:")
print(soup.title.string if soup.title else "No title")

print("\nLooking for reward buttons...\n")

buttons = soup.select("button.reward-button")

print(f"Found {len(buttons)} reward buttons.\n")

for i, button in enumerate(buttons, start=1):
    text = " ".join(button.stripped_strings)

    print("=" * 60)
    print(f"Reward #{i}")
    print(text)
