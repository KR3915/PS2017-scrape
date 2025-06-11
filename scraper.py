import requests
import re
import csv
################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
###################################
URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103"
CSV = "result.csv"
URL_KRAJ_PARAM = "2"
URL_VYBER_PARAM = "2103" 
patterns = {
    "obce_jmeno": r'<td class="overflow_name".*?>(.*?)</td>',
    "obec_kod": r'<a href="ps311\?.*?xobec=(\d+?)&amp;.*?">\d+?</a>'
    }

class Obce:
    def __init__(self, name, kod, url):
        self.name = name
        self.kod = kod
        self.url = url

class Strana:
    def __init__(self, name, hlasy ):
        self.name = name
        self.hlasy = hlasy

class VysledkyStrany:
    def __init__(self, obec, strana, hlasy):
        self.obec = obec
        self.strana = strana
        self.hlasy = hlasy

def ziskej_obecna_data(url):
    r = requests.get(url)
    html = r.text
    list_jmen = re.findall(patterns["obce_jmeno"], html)
    list_kodu = re.findall(patterns["obec_kod"], html)
    if len(list_jmen) == len(list_kodu):
        print(f"Nalezena jména obcí: {len(list_jmen)}, Nalezené kódy obcí: {len(list_kodu)}")
        obce_list = list(zip(list_jmen, list_kodu))
        return obce_list
    else:
        print("Chyba: Počet nalezených jmen a kódů obcí se neshoduje.")
        return []

def ziskej_info(url):
    obce_data_list = ziskej_obecna_data(url)

    list_of_obec_objects = [] 
    if obce_data_list:
        for jmeno, kod in obce_data_list:
            obec_detail_url = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={URL_KRAJ_PARAM}&xobec={kod}&xvyber={URL_VYBER_PARAM}"
            current_obec_obj = Obce(name=jmeno, kod=kod, url=obec_detail_url)
            list_of_obec_objects.append(current_obec_obj)
            print(f"Vytvořen objekt: Jméno='{current_obec_obj.name}', Kód='{current_obec_obj.kod}', URL='{current_obec_obj.url}'")
        return list_of_obec_objects
    else:
        print("Nelze vytvořit objekty Obce, protože ziskej_obecna_data vrátila chybu.")
        return []

def parse_vysledky_stran(html, obec_obj):
    """
    Najde všechny strany a jejich hlasy v HTML jedné obce.
    Vrací seznam objektů vysledkystrany.
    """
    # Najdi všechny řádky s výsledky stran
    pattern = re.compile(
        r'<td class="cislo" headers="t1sa1 t1sb1">(\d+)</td>\s*'
        r'<td class="overflow_name" headers="t1sa1 t1sb2">(.*?)</td>\s*'
        r'<td class="cislo" headers="t1sa2 t1sb3">(\d+)</td>',
        re.DOTALL
    )
    vysledky = []
    for match in pattern.finditer(html):
        # číslo strany = match.group(1) (nepoužíváme)
        jmeno_strany = match.group(2).strip()
        pocet_hlasu = int(match.group(3))
        strana_obj = Strana(jmeno_strany, pocet_hlasu) # Použití opraveného názvu třídy
        vysledek = VysledkyStrany(obec_obj, strana_obj, pocet_hlasu) # Použití opraveného názvu třídy
        vysledky.append(vysledek)
        print(f"Obec: {obec_obj.name}, Strana: {jmeno_strany}, Hlasy: {pocet_hlasu}")
    return vysledky

def process_all_obec_urls(obce_objects):
    """
    Projde všechny objekty Obce, stáhne HTML jejich stránky,
    vytáhne výsledky stran a uloží je do objektů.
    """
    vsechny_vysledky = []
    for obec in obce_objects:
        print(f"Zpracovávám obec: {obec.name}, URL: {obec.url}")
        response = requests.get(obec.url)
        html = response.text
        # print(html) # Zakomentováno pro přehlednější výstup
        vysledky = parse_vysledky_stran(html, obec)
        vsechny_vysledky.extend(vysledky)
        print("\n---\n")
    return vsechny_vysledky

def save_to_csv(data, filename):
    """
    Uloží data do CSV souboru v širokém formátu.
    Každá obec bude mít jeden řádek a každá strana svůj sloupec.
    'data' je seznam objektů VysledkyStrany.
    """
    if not data:
        print("Žádná data k uložení.")
        return

    print(f"Připravuji data pro uložení do souboru: {filename}")
    
    # Shromáždit všechny unikátní názvy stran pro hlavičku
    party_names = sorted(list(set(vysledek.strana.name for vysledek in data)))
    
    # Připravit data: klíč je (kod_obce, nazev_obce), hodnota je slovník {nazev_strany: hlasy}
    obce_data = {}
    for vysledek in data:
        obec_key = (vysledek.obec.kod, vysledek.obec.name)
        if obec_key not in obce_data:
            obce_data[obec_key] = {}
        obce_data[obec_key][vysledek.strana.name] = vysledek.hlasy

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Zápis hlavičky: Kód obce, Název obce, pak všechny názvy stran
        header = ['Obec_Kod', 'Obec_Nazev'] + party_names
        writer.writerow(header)
        
        # Zápis dat pro každou obec
        for (kod, nazev), hlasy_stran in obce_data.items():
            row = [kod, nazev] + [hlasy_stran.get(party_name, 0) for party_name in party_names]
            writer.writerow(row)
            
    print(f"Data byla úspěšně uložena do {filename}")

def main():
    all_obce_objects = ziskej_info(URL)
    
    if all_obce_objects:
        final_results = process_all_obec_urls(all_obce_objects)
        if final_results:
            save_to_csv(final_results, CSV)
        else:
            print("Nebyla získána žádná data o výsledcích stran.")
    else:
        print("Nebyly vytvořeny žádné objekty obcí.")
main()
