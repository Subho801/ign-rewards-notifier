import json
import os
from datetime import datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

# ==========================
# Configuration
# ==========================

URL = "https://www.ign.com/rewards"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

DB_FILE = "posted_rewards.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}

# Replace these with your own images
AUTHOR_ICON = "https://file.garden/afbSsuts32dZ5wSl/images%20(3).png"
FOOTER_ICON = "https://files.catbox.moe/qttqpy.png"

EMBED_COLOR = 0xBF1313


# ==========================
# Database
# ==========================

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


# ==========================
# Helpers
# ==========================

def discord_timestamp(date_string):
    """
    Converts:
    08.03.2026 at 10:30AM

    into

    <t:UNIX:F>
    <t:UNIX:R>

    IGN uses Pacific Time.
    """

    if not date_string or date_string == "Unknown":
        return "Unknown"

    try:
        dt = datetime.strptime(
            date_string,
            "%m.%d.%Y at %I:%M%p"
        )

        dt = dt.replace(
            tzinfo=ZoneInfo("America/Los_Angeles")
        )

        unix = int(dt.timestamp())

        return (
            f"<t:{unix}:F>\n"
            f"(<t:{unix}:R>)"
        )

    except Exception:
        return date_string


def availability_text(text):
    if not text:
        return "Unknown"

    return text


def fix_image_url(url):

    if not url:
        return ""

    return urljoin(URL, url)

def send_discord(title, image, end_date, availability):

    if not WEBHOOK:
        raise RuntimeError("DISCORD_WEBHOOK environment variable is missing.")

    embed = {
        "author": {
    "name": "IGN Rewards",
    "icon_url": AUTHOR_ICON
},

"title": title,
"url": URL,
        "color": EMBED_COLOR,

        "fields": [
            {
                "name": "⏰ Ends",
                "value": discord_timestamp(end_date),
                "inline": True
            },
            {
                "name": "Status",
                "value": availability_text(availability),
                "inline": True
            }
        ],

        "image": {
            "url": fix_image_url(image)
        },

        "footer": {
            "text": "Subho's IGN Rewards Informer",
            "icon_url": FOOTER_ICON
        },


        "url": URL
    }

    try:
        response = requests.post(
            WEBHOOK,
            json={
                "embeds": [embed]
            },
            timeout=30
        )

        if response.status_code not in (200, 204):
            print(
                f"Discord webhook failed "
                f"({response.status_code})"
            )
            print(response.text)

    except Exception as e:
        print("Discord Error:", e)

    # ==========================
# Main
# ==========================

print("Downloading IGN Rewards...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

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

    image_url = ""

    if image:
        image_url = image.get("src", "")

    end = (
        end_date.get_text(strip=True)
        if end_date
        else "Unknown"
    )

    region = (
        availability.get_text(strip=True)
        if availability
        else "Unknown"
    )

    print(f"NEW: {reward}")

    send_discord(
        reward,
        image_url,
        end,
        region
    )

    posted.append(reward)

    new_count += 1

save_posted(posted)

print(f"\nPosted {new_count} new reward(s).")
