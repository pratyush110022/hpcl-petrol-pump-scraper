# HPCL Fuel Outlet Scraper

Browser-based Python automation for collecting HPCL outlet details from location-listing pages and building state-wise and consolidated CSV datasets.

## How it works

1. Reads an input CSV with the columns State and URL.
2. Opens each configured listing URL with Playwright Chromium in headless mode.
3. Requests sequential listing pages by adding a page number to the base URL.
4. Parses outlet cards with BeautifulSoup and follows each available map/detail link to read opening/status text and directions links.
5. Saves a deduplicated CSV for each input state and a consolidated master file.

## Output data

The script standardizes these columns:

- Brand, Dealer_Name, and Address
- City, State, and Pincode
- Phone
- Latitude and Longitude
- Status
- Google_Map_URL

The output folder contains one <State>_HPCL.csv file for each state with records, plus All_States_HPCL.csv. CSVs are saved with UTF-8 BOM encoding for spreadsheet compatibility.

## Repository contents

- hpcl_scraper_CSV.py — scraper entry point
- Input CSV examples — source state and URL lists
- A sample outlet CSV — example output data

## Requirements

- Python 3.10 or a compatible version
- Playwright
- pandas
- beautifulsoup4
- lxml

Install and prepare the browser:

    python -m venv .venv
    .venv/Scripts/Activate.ps1
    pip install playwright pandas beautifulsoup4 lxml
    playwright install chromium

## Configuration and run

Edit the INPUT_CSV and OUTPUT_FOLDER constants near the beginning of hpcl_scraper_CSV.py. They currently contain absolute Windows paths from the original workstation. Point INPUT_CSV to an input CSV in your local checkout and choose a writable output folder.

The input file must contain:

| Column | Purpose |
|---|---|
| State | State label assigned to records from that input row |
| URL | Base listing URL used to request paginated results |

Run:

    python hpcl_scraper_CSV.py

## Notes

- A state file is written only when records were collected for that state; the master file is written when the run has data.
- Website markup, pagination, or detail-page links can change and may require selector updates.
- Use authorized collection practices and check the website's terms and applicable rules before using or redistributing the data.
