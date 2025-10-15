from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("start-maximized")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(120)

# ---- SCRAPE FUNCTION ----
# Scrapes batting and pitching tables for a given league and year.
def scrape_league(url, year, league_abbr):
    try:
        driver.get(url)
        time.sleep(5)

        tables = driver.find_elements(By.TAG_NAME, "table")
        table_names = [f"batting_{year}_{league_abbr}",
                       f"pitching_{year}_{league_abbr}"]

        for i in range(2):
            table = tables[i]
            rows = []
            for tr in table.find_elements(By.TAG_NAME, "tr"):
                cells = [td.text.strip()
                         for td in tr.find_elements(By.TAG_NAME, "td")]
                if len(cells) == 5:
                    rows.append(cells)

            headers = ["Statistic", "Name", "Team", "#", "Top 25"]
            df = pd.DataFrame(rows, columns=headers)

            df["Year"] = year
            df["League"] = league_abbr

            df.to_csv(f"data/{table_names[i]}.csv", index=False)
            print(f"Saved {table_names[i]}.csv")

    except Exception as e:
        print(f"Couldn't scrape {league_abbr} {year} page")
        print(f"Exception: {type(e).__name__} - {e}")


# ---- RUN SCRAPERS ----
try:
    leagues = {"AL": "a", "NL": "n"}
    years = [2023, 2024]

    for year in years:
        for league_abbr, letter in leagues.items():
            print(f"\n=== Scraping {year} {league_abbr} ===")
            url = f"https://www.baseball-almanac.com/yearly/yr{year}{letter}.shtml"
            scrape_league(url, year, league_abbr)

finally:
    driver.quit()
    print("\nScraping finished and browser closed.")
