import json
import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.ign.com/rewards"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}

DB_FILE = "posted_rewards.json"


def load_posted():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_posted(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def send_discord(title, image, end_date, availability):

    embed = {
        "title": "🎁 New IGN Reward",
        "color": 0xE50914,
        "fields": [
            {
                "name": "Reward",
                "value": title,
                "inline": False
            },
            {
                "name": "Ends",
                "value": end_date,
                "inline": True
            },
            {
                "name": "Availability",
                "value": availability,
                "inline": True
            }
        ],
        "url": URL,
        "image": {
            "url": image
        },
        "footer": {
            "text": "IGN Rewards Notifier"
        }
    }

    requests.post(
        WEBHOOK,
        json={
            "embeds": [embed]
        },
        timeout=30
    )


print("Downloading IGN Rewards...")

response = requests.get(URL, headers=HEADERS, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

cards = soup.select('[data-cy="rewardCard"]')

print(f"Found {len(cards)} rewards")

posted = load_posted()

new_count = 0

for card in cards:

    title = card.select_one('[data-cy="cardTitle"]')
    image = card.select_one('[data-cy="rewardImg"] img')
    end_date = card.select_one('[data-cy="endDate"]')
    availability = card.select_one('[data-cy="availability"]')

    if not title:
        continue

    reward = title.get_text(strip=True)

    if reward in posted:
        print(f"Skipping: {reward}")
        continue

    print(f"NEW: {reward}")

    send_discord(
        reward,
        image.get("src") if image else "",
        end_date.get_text(strip=True) if end_date else "Unknown",
        availability.get_text(strip=True) if availability else "Unknown"
    )

    posted.append(reward)
    new_count += 1

save_posted(posted)

print(f"\nPosted {new_count} new rewards.")
