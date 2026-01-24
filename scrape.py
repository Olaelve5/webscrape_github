import requests
import sqlite3
from datetime import datetime


def setup_database():
    conn = sqlite3.connect("odds_data.db")
    c = conn.cursor()

    # New table specifically for Cycling (Race -> Rider -> Odds)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cycling_odds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_name TEXT,
            rider_name TEXT,
            odds REAL,
            scraped_at TEXT
        )
    """
    )
    conn.commit()
    return conn


def run_scraper():
    # The Tour de France 2026 Winner URL you found
    url = "https://eu1.offering-api.kambicdn.com/offering/v2018/ubdk/betoffer/event/1024452735.json?lang=da_DK&market=DK&channel_id=1&ncid=1769285927747&includeParticipants=true&range_size=1"

    print(f"Fetching Cycling data...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed! Status code: {response.status_code}")
        return

    data = response.json()
    conn = setup_database()
    c = conn.cursor()

    # 1. Get the Race Name
    events = data.get("events", [])
    if not events:
        print("No event info found.")
        return

    race_name = events[0]["name"]  # "General Classification (Tour de France 2026)"
    print(f"Race: {race_name}")

    # 2. Get the Odds (BetOffers)
    bet_offers = data.get("betOffers", [])

    riders_saved = 0

    for offer in bet_offers:
        # We look for the "Winner" market (Vinder)
        # In your JSON, criterion['label'] is "Vinder"
        if offer["criterion"]["label"] in [
            "Vinder",
            "Winner",
            "General Classification",
        ]:

            outcomes = offer["outcomes"]

            for rider in outcomes:
                rider_name = rider["label"]
                raw_odds = rider["odds"]
                real_odds = raw_odds / 1000.0  # Convert 1350 -> 1.35

                # Print the favorite (low odds) to console just to check
                if real_odds < 10.0:
                    print(f"Favorite: {rider_name} @ {real_odds}")

                # Save to DB
                c.execute(
                    """
                    INSERT INTO cycling_odds (race_name, rider_name, odds, scraped_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (race_name, rider_name, real_odds, datetime.now().isoformat()),
                )

                riders_saved += 1

    conn.commit()
    conn.close()
    print(f"--- Saved {riders_saved} riders to database ---")


if __name__ == "__main__":
    run_scraper()
