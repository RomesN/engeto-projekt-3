import csv
import sys
import bs4
import requests


# aguments check
def arg_check() -> tuple:
    # number of arguments
    if len(sys.argv) != 3:
        sys.exit("""Nesprávny počet argumentov! Správne použitie: python Elections_scraper.py
                  \"LINK\" \"JMÉNO_SOUBORU.csv\"""")
    else:
        url = sys.argv[1]
        csv_n = sys.argv[2]
        response = requests.get(url)
        # csv name on the right place
        if csv_n[-4:] != ".csv":
            print(f"Skontroluj správnosť názvu súboru. Názov sa musí končiť výrazom \".csv\"")
            sys.exit()
        # url validity
        if not response.ok:
            print(f"Skontroluj správnosť linku. Odpoveď serveru: \"{response.status_code}: {response.reason}\"")
            sys.exit()

    return csv_n, response.text, url


# creating clean csv file with header
def csv_creation(filename) -> None:
    header = (
        "Kód obce", "Název obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy", "Občanská demokratická strana",
        "Řád národa - Vlastenecká unie", "CESTA ODPOVĚDNÉ SPOLEČNOSTI",
        "Česká str.sociálně demokrat.", "Radostné Česko", "STAROSTOVÉ A NEZÁVISLÍ",
        "Komunistická str.Čech a Moravy", "Strana zelených", "ROZUMNÍ-stop migraci,diktát.EU",
        "Strana svobodných občanů", "Blok proti islam.-Obran.domova", "Občanská demokratická aliance",
        "Česká pirátská strana", "OBČANÉ 2011-SPRAVEDL. PRO LIDI", "Referendum o Evropské unii", "TOP 09",
        "ANO 2011", "SPR-Republ.str.Čsl. M.Sládka", "Křesť.demokr.unie-Čs.str.lid.",
        "Česká strana národně sociální", "REALISTÉ", "SPORTOVCI", "Dělnic.str.sociální spravedl.",
        "Svob.a př.dem.-T.Okamura (SPD)", "Strana Práv Občanů"
    )
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    return None


# Scraping of commune links list
def links_to_scrape(beso) -> list:
    links = []
    tables_to_scrape = beso.find_all("table")
    for table in tables_to_scrape:
        rows = table.children
        for row in filter(lambda x: x != '\n', rows):
            for cell in row.find_all("td"):
                try:
                    class_in = cell.attrs.get("class")[-1]
                    header_in = cell.attrs.get("headers")[-1][-3:]
                except TypeError:
                    class_in = [cell.attrs.get("class")]
                    header_in = cell.attrs.get("headers")[-1][-3:]
                if cell.attrs.get("headers") is not None:
                    # Scraping commune number
                    if class_in == "cislo" and header_in == "sb1":
                        links.append([])
                        links[-1].append(cell.a.string)
                        links[-1].append("https://volby.cz/pls/ps2017nss/" + cell.a.attrs.get("href"))
                    # Scraping commune name if it is link
                    elif header_in == "sb2" and (cell.a is not None):
                        links[-1].append(cell.a.string)
                    # Scraping commune name
                    elif header_in == "sb2" and class_in == "overflow_name":
                        links[-1].append(cell.string)
    return links


# Commune data scraping
def obec_scrape(link_list) -> list:
    link = link_list[1]
    row_to_add = [link_list[0], link_list[2]]
    response = requests.get(link)
    if not response.ok:
        raise requests.HTTPError(f"""Jedna z URLs na \"volby.cz\" nefunguje: \"{response.status_code}: "
                                 {response.reason}\"""")
    soup_com = bs4.BeautifulSoup(response.text, "html.parser")
    tables_to_scrape = soup_com.find_all("table")
    for table in tables_to_scrape:
        rows = table.children
        for row in filter(lambda x: x != '\n', rows):
            for cell in row.find_all("td"):
                cell_cl = cell.attrs.get("class")[0]
                cell_he = cell.attrs.get("headers")[-1]
                if (cell.attrs.get("class") is not None) or (cell.attrs.get("headers") is not None):
                    # Scraping "Voliči v seznamu"
                    if cell_cl == "cislo" and cell_he == "sa2":
                        row_to_add.append(cell.string.replace("\xa0", ""))
                    # Scraping "Vydané obálky"
                    elif cell_cl == "cislo" and cell_he == "sa3":
                        row_to_add.append(cell.string.replace("\xa0", ""))
                    # Scraping "Platné hlasy"
                    elif cell_cl == "cislo" and cell_he == "sa6":
                        row_to_add.append(cell.string.replace("\xa0", ""))
                    # Scraping "Hlasy strany celkem"
                    elif cell_cl == "cislo" and ((cell_he == "t2sb3") or (cell_he == "t1sb3")):
                        row_to_add.append(cell.string.replace("\xa0", ""))
    return row_to_add


# adding data from scraped communes into the file
def row_adding(filename, row) -> None:
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    return None


if __name__ == "__main__":
    csv_name, resp, url_name = arg_check()
    soup = bs4.BeautifulSoup(resp, "html.parser")
    csv_creation(csv_name)
    print(f"SŤAHUJEM Z VYBRANÉHO URL: {url_name}")
    links_list = links_to_scrape(soup)
    print(f"UKLADÁM DO SÚBORU: {csv_name}")
    for r in range(0, len(links_list)):
        row_t_add = obec_scrape(links_list[r])
        row_adding(csv_name, row_t_add)
    print("KONČÍM Election-scraper.")

 
