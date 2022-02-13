import sys
from bs4 import BeautifulSoup as BeSo
import requests


# aguments check
def arg_check() -> tuple:
    if len(sys.argv) != 3:
        sys.exit("""Nesprávny počet argumentov! Správne použitie: python Elections_scraper.py
                  \"LINK\" \"JMÉNO_SOUBORU.csv\"""")
    else:
        url = sys.argv[1]
        csv_n = sys.argv[2]
        response = requests.get(url)
        if csv_n[-4:] != ".csv":
            print(f"Skontroluj správnosť názvu súboru. Názov sa musí končiť výrazov \".csv\"")
        if not response.ok:
            print(f"Skontroluj správnosť linku. Odpoveď serveru: \"{response.status_code}: {response.reason}\"")
            sys.exit()

    return csv_n, response


# making BeautifulSoup
def make_soup(response) -> BeSo.BeautifulSoup:
    soup_result = BeSo(response.text, "html.parser")
    return soup_result


# creating csv file
def make_csv():
    return None


if __name__ == "__main__":
    csv_name = arg_check()[0]
    resp = arg_check()[1]
    print(resp)
    soup = make_soup(resp)
