import requests
import re
import csv
################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
###################################
#----------------------html----------------------
#<td class="cislo" headers="sa1 sb1">1</td>
#<td class="cislo" headers="sa1 sb2">1</td>
#<td class="cislo" headers="sa1 sb3">100,00</td>
#<td class="cislo" headers="sa2" data-rel="L1">262</td>
#<td class="cislo" headers="sa3" data-rel="L1">181</td>
#<td class="cislo" headers="sa4">69,08</td>
#<td class="cislo" headers="sa5" data-rel="L1">181</td>
#<td class="cislo" headers="sa6" data-rel="L1">181</td>
#<td class="cislo" headers="sa7">100,00</td>
#-------------------------------------------------
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
        self.volici_v_seznamu = None
        self.vydane_obalky = None
        self.platne_hlasy = None

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

def parse_summary_stats(html):
    """
    Extrahuje souhrnné statistiky (voliči, obálky, platné hlasy) z HTML obce.
    Vrací slovník se statistikami.
    """
    stats = {
        'Volic_v_seznamu': 0,
        'Vydane_obalky': 0,
        'Platne_hlasy': 0
    }
    
    # Voliči v seznamu (headers="sa2")
    match_volici = re.search(r'<td class="cislo" headers="sa2"[^>]*>([^<]+)</td>', html)
    if match_volici:
        stats['Volic_v_seznamu'] = int(match_volici.group(1).replace('&nbsp;', '').strip())

    # Vydané obálky (headers="sa3")
    match_obalky = re.search(r'<td class="cislo" headers="sa3"[^>]*>([^<]+)</td>', html)
    if match_obalky:
        stats['Vydane_obalky'] = int(match_obalky.group(1).replace('&nbsp;', '').strip())

    # Platné hlasy (headers="sa6")
    match_platne = re.search(r'<td class="cislo" headers="sa6"[^>]*>([^<]+)</td>', html)
    if match_platne:
        stats['Platne_hlasy'] = int(match_platne.group(1).replace('&nbsp;', '').strip())
        
    return stats

def parse_vysledky_stran(html, obec_obj):
    """
    Najde všechny strany a jejich hlasy v HTML jedné obce.
    Vrací seznam objektů vysledkystrany.
    """
    # Najdi všechny řádky s výsledky stran
    pattern = re.compile(
        r'<td class="cislo" headers="t1sa1 t1sb1">\s*(\d+)\s*</td>\s*'  # Group 1: Party number
        r'<td class="overflow_name" headers="t1sa1 t1sb2">([^<]*)</td>\s*' # Group 2: Party name (any char except <)
        r'<td class="cislo" headers="t1sa2 t1sb3">([^<]*)</td>'  # Group 3: Votes (any char except <)
    )
    vysledky = []
    for match in pattern.finditer(html):
        # číslo strany = match.group(1) (nepoužíváme)
        jmeno_strany = match.group(2).strip()
        pocet_hlasu_str = match.group(3).replace('&nbsp;', '').strip() # Nahradit &nbsp; a odstranit mezery
        try:
            pocet_hlasu = int(pocet_hlasu_str)
        except ValueError:
            print(f"Chyba: Nelze převést počet hlasů '{pocet_hlasu_str}' na číslo pro stranu '{jmeno_strany}' v obci '{obec_obj.name}'. Přeskakuji stranu.")
            continue
            
        strana_obj = Strana(jmeno_strany, pocet_hlasu)
        vysledek = VysledkyStrany(obec_obj, strana_obj, pocet_hlasu)
        vysledky.append(vysledek)
        # print(f"Obec: {obec_obj.name}, Strana: {jmeno_strany}, Hlasy: {pocet_hlasu}") # Můžete odkomentovat pro ladění
    return vysledky

def process_all_obec_urls(obce_objects):
    """
    Projde všechny objekty Obce, stáhne HTML jejich stránky,
    vytáhne výsledky stran a uloží je do objektů.
    """
    vsechny_vysledky = []
    first_obec_processed = False # Sledování, zda byla první obec již zpracována
    for obec in obce_objects:
        print(f"Zpracovávám obec: {obec.name}, URL: {obec.url}")
        response = requests.get(obec.url)
        html = response.text

        summary_data = parse_summary_stats(html)
        obec.volici_v_seznamu = summary_data.get('Volic_v_seznamu')
        obec.vydane_obalky = summary_data.get('Vydane_obalky')
        obec.platne_hlasy = summary_data.get('Platne_hlasy')

        if not first_obec_processed:
            print(f"\n--- Prvních 1000 znaků HTML pro obec {obec.name}: ---\n")
            print(html[:10000])
            # first_obec_processed = True # Můžete odkomentovat, pokud chcete výpis jen pro první obec
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
    summary_stat_keys = ['registered', 'envelopes', 'valid']
    
    # Připravit data: klíč je (kod_obce, nazev_obce), 
    # hodnota je slovník obsahující souhrnné statistiky a hlasy stran
    obce_data_restructured = {}
    for vysledek in data:
        obec_obj = vysledek.obec
        obec_key = (obec_obj.kod, obec_obj.name)
        if obec_key not in obce_data_restructured:
            obce_data_restructured[obec_key] = {
                'Volic_v_seznamu': obec_obj.volici_v_seznamu,
                'Vydane_obalky': obec_obj.vydane_obalky,
                'Platne_hlasy': obec_obj.platne_hlasy,
                'party_votes': {} 
            }
        obce_data_restructured[obec_key]['party_votes'][vysledek.strana.name] = vysledek.hlasy

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Zápis hlavičky: Kód obce, Název obce, souhrnné statistiky, pak všechny názvy stran
        header = ['Obec_Kod', 'Obec_Nazev'] + summary_stat_keys + party_names
        writer.writerow(header)
        
        # Zápis dat pro každou obec
        for (kod, nazev), combined_data in obce_data_restructured.items():
            row = [kod, nazev] + \
                  [combined_data.get(key, 0) for key in summary_stat_keys] + \
                  [combined_data['party_votes'].get(party_name, 0) for party_name in party_names]
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
