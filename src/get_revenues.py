"""Pull/ clean revenue pdfs from Nevada Gaming Board Site."""

from pathlib import Path
import requests
import subprocess
from bs4 import BeautifulSoup
import time
import camelot


SITE_URL = "https://gaming.nv.gov/"
GAMING_REVENUE_URL = SITE_URL + "index.aspx?page=149"
DATA_DIRECTORY = Path(__file__).parent.resolve().parent / "data"


def make_data_directories():
    """Set up pdfs and csv directories."""
    (DATA_DIRECTORY / "pdfs").mkdir(parents=True, exist_ok=True)
    (DATA_DIRECTORY / "csvs").mkdir(parents=True, exist_ok=True)
    return


def get_main_page() -> BeautifulSoup:
    """Get html from monthly revenue pdf list."""
    response = requests.get(GAMING_REVENUE_URL)
    soup = BeautifulSoup(response.content)
    return soup


def clean_month_str(raw_month:str) -> str:
    """Months are gross, clean them."""
    clean_month = raw_month.strip().replace("\xa0", " ").replace("\n", "").replace(" ", "_").upper()
    assert len(clean_month) <= 9
    return clean_month


def get_pdf_urls(soup: BeautifulSoup) -> dict:
    """Parse monthly revenue page for (month, urls for pdf reports)."""
    month_url_map = {}
    for row in soup.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) == 4: # want the links from the table with 4 columns
            cleaned_month = clean_month_str(str(tds[0].text))
            link = tds[-1].find("a") # last column holds the pdf link
            if link:
                link_url = link.get("href")
                month_url_map[cleaned_month] = SITE_URL + link_url
    return month_url_map


def download_pdfs(pdf_url_map: dict):
    """Download pdfs from Nevada Gaming Board Site."""
    for month, url in pdf_url_map.items():
        print(f"Downloading data for {month}.")
        month_file_path = DATA_DIRECTORY / "pdfs" / f"{month}_gaming_revenues.pdf"
        command = f"curl {url} -o {month_file_path}"
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL)
        time.sleep(0.1)
    print("Done downloading data.")
    return

def convert_pdfs_to_csvs(page):
    pdfs_path = DATA_DIRECTORY / "pdfs"
    csvs_path = DATA_DIRECTORY / "csvs"
    pdfs = list(pdfs_path.iterdir())
    tabula_path = Path(__file__).parent.resolve().parent.parent / "tabula-java"
    jar_path = tabula_path / "target" / "tabula-1.0.6-SNAPSHOT-jar-with-dependencies.jar"
    for pdf in pdfs:
        if "APR_2020" in str(pdf) or "MAY_2020" in str(pdf):
            continue
        print(f"Writing data for {pdf}")
        tables = camelot.read_pdf(str(pdf), pages="15", flavor="stream")
        csv_path = str(pdf).split("/")[-1].replace("pdf", "csv")
        tables[0].df.to_csv(csvs_path/ csv_path, index=None)
    print("PDFs converted to CSVs.")
    return


def main():
    #make_data_directories()
    #soup = get_main_page()
    #pdf_url_map = get_pdf_urls(soup)
    #download_pdfs(pdf_url_map)
    convert_pdfs_to_csvs(page=15)

if __name__ == "__main__":
    main()
