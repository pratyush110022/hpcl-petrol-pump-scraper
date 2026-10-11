"""
HPCL Petrol Pump Scraper (State-wise Output)

Requirements:
    pip install playwright pandas beautifulsoup4 lxml tqdm
    playwright install chromium

Input CSV:
State,URL

Example:
Andhra Pradesh,https://petrolpump.hpretail.in/location/andhra-pradesh

Output:
State_Wise_Output/
    Andhra_Pradesh_HPCL.csv
    Odisha_HPCL.csv
    Maharashtra_HPCL.csv
    ...
    All_States_HPCL.csv
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# ==========================================================
# FILE PATHS
# ==========================================================
INPUT_CSV = r"C:\Users\prdas4\Downloads\2025_Projects\2025_H1\H1_2025\2-Junks Check\Petrol Pump\HP\input - City.csv"

OUTPUT_FOLDER = r"C:\Users\prdas4\Downloads\2025_Projects\2025_H1\H1_2025\2-Junks Check\Petrol Pump\HP\State_Wise_Output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# OUTPUT COLUMNS
# ==========================================================
COLUMNS = [
    "Brand",
    "Dealer_Name",
    "Address",
    "City",
    "State",
    "Pincode",
    "Phone",
    "Latitude",
    "Longitude",
    "Status",
    "Google_Map_URL"
]


# ==========================================================
# PARSE LISTING PAGE
# ==========================================================
def parse_listing(page):
    soup = BeautifulSoup(page.content(), "lxml")

    rows = []

    for box in soup.select("div.store-info-box"):
        try:
            lat = box.select_one(".outlet-latitude")
            lon = box.select_one(".outlet-longitude")

            brand = box.select_one("li.outlet-name a")

            dealer = None
            info_texts = box.select("div.info-text")
            if len(info_texts) > 1:
                dealer = info_texts[1]

            addr = box.select_one("li.outlet-address .info-text")

            address = ""
            city = ""
            pin = ""

            if addr:
                lines = list(addr.stripped_strings)

                if lines:
                    address = ", ".join(lines)

                    if len(lines) >= 2:
                        city = lines[-2]

                    last_line = lines[-1]

                    if "-" in last_line:
                        parts = last_line.split("-")
                        city = parts[0].strip()
                        pin = parts[1].strip()

            phone = box.select_one("li.outlet-phone a")
            map_link = box.select_one("a.btn-map")

            rows.append({
                "Brand": brand.get_text(strip=True) if brand else "",
                "Dealer_Name": dealer.get_text(strip=True) if dealer else "",
                "Address": address,
                "City": city,
                "State": "",
                "Pincode": pin,
                "Phone": phone.get_text(strip=True) if phone else "",
                "Latitude": lat.get("value", "") if lat else "",
                "Longitude": lon.get("value", "") if lon else "",
                "MapPage": map_link.get("href", "") if map_link else ""
            })

        except Exception as e:
            print("Parse error:", e)

    return rows


# ==========================================================
# PARSE DETAIL PAGE
# ==========================================================
def fetch_detail(page, url):
    status = ""
    gmap = ""

    try:
        page.goto(url, wait_until="networkidle", timeout=60000)

        soup = BeautifulSoup(page.content(), "lxml")

        st = soup.select_one("li.store-clock span")
        if st:
            status = st.get_text(" ", strip=True)

        gm = soup.select_one("a.action-direction")
        if gm:
            gmap = gm.get("href", "")

    except Exception as e:
        print("Detail error:", e)

    return status, gmap


# ==========================================================
# MAIN
# ==========================================================
def main():

    inputs = pd.read_csv(INPUT_CSV)

    all_data = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for _, row in inputs.iterrows():

            state = str(row["State"]).strip()
            base_url = str(row["URL"]).strip()

            print("\n" + "=" * 80)
            print(f"Processing State : {state}")
            print("=" * 80)

            state_records = []

            page_no = 1

            while True:

                listing_url = f"{base_url}?page={page_no}"

                print(f"Page {page_no} : {listing_url}")

                try:
                    page.goto(
                        listing_url,
                        wait_until="networkidle",
                        timeout=60000
                    )
                except:
                    break

                items = parse_listing(page)

                if not items:
                    print("No more records found.")
                    break

                for item in items:

                    item["State"] = state

                    if item.get("MapPage"):

                        status, gmap = fetch_detail(
                            page,
                            item["MapPage"]
                        )

                        item["Status"] = status
                        item["Google_Map_URL"] = gmap

                    else:
                        item["Status"] = ""
                        item["Google_Map_URL"] = ""

                    item.pop("MapPage", None)

                    state_records.append(item)
                    all_data.append(item)

                page_no += 1

                time.sleep(1)

            # ==========================================
            # SAVE CURRENT STATE FILE
            # ==========================================
            if state_records:

                state_df = pd.DataFrame(state_records)

                for col in COLUMNS:
                    if col not in state_df.columns:
                        state_df[col] = ""

                state_df = (
                    state_df[COLUMNS]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )

                safe_state = (
                    state.replace("/", "_")
                    .replace("\\", "_")
                    .replace(" ", "_")
                )

                state_file = os.path.join(
                    OUTPUT_FOLDER,
                    f"{safe_state}_HPCL.csv"
                )

                state_df.to_csv(
                    state_file,
                    index=False,
                    encoding="utf-8-sig"
                )

                print(
                    f"Saved {len(state_df)} records -> {state_file}"
                )

        browser.close()

    # ======================================================
    # SAVE MASTER FILE
    # ======================================================
    if all_data:

        master_df = pd.DataFrame(all_data)

        for col in COLUMNS:
            if col not in master_df.columns:
                master_df[col] = ""

        master_df = (
            master_df[COLUMNS]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        master_file = os.path.join(
            OUTPUT_FOLDER,
            "All_States_HPCL.csv"
        )

        master_df.to_csv(
            master_file,
            index=False,
            encoding="utf-8-sig"
        )

        print("\n" + "=" * 80)
        print(f"Total Records : {len(master_df)}")
        print(f"Master File   : {master_file}")
        print("=" * 80)


if __name__ == "__main__":
    main()