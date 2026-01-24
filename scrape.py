import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_URI")


def run_scraper():
    # Tour de France 2026 Winner (GC) URL
    url = "https://eu1.offering-api.kambicdn.com/offering/v2018/ubdk/betoffer/event/1024452735.json?lang=da_DK&market=DK&channel_id=1&ncid=1769285927747&includeParticipants=true&range_size=1"

    print(f"Fetching GC Odds...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed! Status code: {response.status_code}")
            return

        data = response.json()

        # 1. Get Event Info
        events = data.get("events", [])
        if not events:
            print("No event info found.")
            return

        race_name = events[0][
            "name"
        ]  # e.g. "General Classification (Tour de France 2026)"
        print(f"Race: {race_name}")

        # 2. Get Odds
        bet_offers = data.get("betOffers", [])
        rows_to_insert = []

        for offer in bet_offers:
            # We strictly look for the Winner market
            if offer["criterion"]["label"] in [
                "Vinder",
                "Winner",
                "General Classification",
            ]:

                for rider in offer["outcomes"]:
                    rider_name = rider["label"]
                    real_odds = rider["odds"] / 1000.0

                    # Hardcoded 'GC_WINNER' and None for stage_number
                    rows_to_insert.append(
                        (
                            race_name,
                            "GC_WINNER",
                            None,
                            rider_name,
                            real_odds,
                            datetime.now(),
                        )
                    )

                    # Print favorites to console just for verification
                    if real_odds < 5.0:
                        print(f"Favorite: {rider_name} @ {real_odds}")

        # 3. Save to Supabase
        if rows_to_insert:
            conn = psycopg2.connect(DB_URI)
            cur = conn.cursor()

            # Efficient bulk insert
            args_str = ",".join(
                cur.mogrify("(%s,%s,%s,%s,%s,%s)", x).decode("utf-8")
                for x in rows_to_insert
            )

            cur.execute(
                """
                INSERT INTO cycling_odds 
                (race_name, market_type, stage_number, rider_name, odds, scraped_at) 
                VALUES 
            """
                + args_str
            )

            conn.commit()
            cur.close()
            conn.close()
            print(f"--- SUCCESS: Saved {len(rows_to_insert)} rows to Supabase ---")
        else:
            print("No odds found to save.")

    except Exception as e:
        print(f"Script Error: {e}")


if __name__ == "__main__":
    run_scraper()
