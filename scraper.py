import requests
import re
import csv
import sys
"""
scraper.py: PS-2017 scraper
author: Ondřej Brdek
email: ondrej.brdek@gmail.com discord: #ulaviceditestalozplnahrdlakricel
"""
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

patterns = {
    "obce_jmeno": r'<td class="overflow_name".*?>(.*?)</td>',
    "obec_kod": r'<a href="ps311\?.*?xobec=(\d+?)&amp;.*?">\d+?</a>',
}

class Obce:
    def __init__(self, name, kod, url):
        self.name = name
        self.kod = kod
        self.url = url
        self.registered = None  # Voliči v seznamu
        self.envelopes = None   # Vydané obálky
        self.valid = None       # Platné hlasy

class Strana:
    def __init__(self, name, hlasy ):
        self.name = name
        self.hlasy = hlasy

class VysledkyStrany:
    def __init__(self, obec, strana, hlasy):
        self.obec = obec
        self.strana = strana
        self.hlasy = hlasy

def ziskej_zakladni_data_obci(url):
    try:
        r = requests.get(url)
        r.raise_for_status()  # Zkontroluje HTTP chyby
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování URL {url}: {e}")
        return []
        
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

def ziskej_informace_o_obcich(url_uzemniho_celku):
    obce_data_list = ziskej_zakladni_data_obci(url_uzemniho_celku)
    list_of_obec_objects = [] 

    # Extrahovat xkraj a xnumnuts (xvyber) z hlavní URL pro detailní URL obcí
    match_kraj = re.search(r"xkraj=(\d+)", url_uzemniho_celku)
    match_numnuts = re.search(r"xnumnuts=(\d+)", url_uzemniho_celku)

    if not match_kraj or not match_numnuts:
        print("Chyba: Nelze extrahovat 'xkraj' nebo 'xnumnuts' z poskytnuté URL.")
        return []
        
    url_kraj_param = match_kraj.group(1)
    url_vyber_param = match_numnuts.group(1)

    if obce_data_list:
        for jmeno, kod in obce_data_list:
            obec_detail_url = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={url_kraj_param}&xobec={kod}&xvyber={url_vyber_param}"
            current_obec_obj = Obce(name=jmeno, kod=kod, url=obec_detail_url)
            list_of_obec_objects.append(current_obec_obj)
            # print(f"Vytvořen objekt: Jméno='{current_obec_obj.name}', Kód='{current_obec_obj.kod}', URL='{current_obec_obj.url}'")
        return list_of_obec_objects
    else:
        print("Nelze vytvořit objekty Obce, protože ziskej_obecna_data vrátila chybu nebo žádná data.")
        return []

def parsuj_souhrnne_statistiky(html):
    """
    Extrahuje souhrnné statistiky (voliči, obálky, platné hlasy) z HTML obce.
    Vrací slovník se statistikami.
    """
    stats = {
        'registered': 0,
        'envelopes': 0,
        'valid': 0
    }
    
    # Voliči v seznamu (headers="sa2")
    match_volici = re.search(r'<td class="cislo" headers="sa2"[^>]*>([^<]+)</td>', html)
    if match_volici:
        try:
            stats['registered'] = int(match_volici.group(1).replace('&nbsp;', '').strip())
        except ValueError:
            print(f"Chyba: Nelze převést 'registered' na číslo: {match_volici.group(1)}")


    # Vydané obálky (headers="sa3")
    match_obalky = re.search(r'<td class="cislo" headers="sa3"[^>]*>([^<]+)</td>', html)
    if match_obalky:
        try:
            stats['envelopes'] = int(match_obalky.group(1).replace('&nbsp;', '').strip())
        except ValueError:
            print(f"Chyba: Nelze převést 'envelopes' na číslo: {match_obalky.group(1)}")

    # Platné hlasy (headers="sa6")
    match_platne = re.search(r'<td class="cislo" headers="sa6"[^>]*>([^<]+)</td>', html)
    if match_platne:
        try:
            stats['valid'] = int(match_platne.group(1).replace('&nbsp;', '').strip())
        except ValueError:
            print(f"Chyba: Nelze převést 'valid' na číslo: {match_platne.group(1)}")
            
    return stats

def parsuj_vysledky_politickych_stran(html, obec_obj):
    pattern = re.compile(
        r'<td class="cislo" headers="t1sa1 t1sb1">\s*(\d+)\s*</td>\s*' 
        r'<td class="overflow_name" headers="t1sa1 t1sb2">([^<]*)</td>\s*' 
        r'<td class="cislo" headers="t1sa2 t1sb3">([^<]*)</td>'  
    )
    vysledky = []
    for match in pattern.finditer(html):
        jmeno_strany = match.group(2).strip()
        pocet_hlasu_str = match.group(3).replace('&nbsp;', '').strip() 
        try:
            pocet_hlasu = int(pocet_hlasu_str)
        except ValueError:
            print(f"Chyba: Nelze převést počet hlasů '{pocet_hlasu_str}' na číslo pro stranu '{jmeno_strany}' v obci '{obec_obj.name}'. Přeskakuji stranu.")
            continue
            
        strana_obj = Strana(jmeno_strany, pocet_hlasu)
        vysledek = VysledkyStrany(obec_obj, strana_obj, pocet_hlasu)
        vysledky.append(vysledek)
    return vysledky

def zpracuj_vsechny_url_obci(obce_objects):
    vsechny_vysledky = []
    # first_obec_processed = False 
    for obec_index, obec in enumerate(obce_objects):
        print(f"Zpracovávám obec {obec_index + 1}/{len(obce_objects)}: {obec.name}, URL: {obec.url}")
        try:
            response = requests.get(obec.url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Chyba při stahování detailu obce {obec.name} ({obec.url}): {e}")
            continue # Přeskočit tuto obec a pokračovat další
            
        html = response.text

        summary_data = parsuj_souhrnne_statistiky(html)
        obec.registered = summary_data.get('registered')
        obec.envelopes = summary_data.get('envelopes')
        obec.valid = summary_data.get('valid')

        # if not first_obec_processed:
        #     print(f"\n--- Prvních 10000 znaků HTML pro obec {obec.name}: ---\n")
        #     print(html[:10000])
        #     first_obec_processed = True 
        vysledky_stran_pro_obec = parsuj_vysledky_politickych_stran(html, obec)
        if not vysledky_stran_pro_obec and html: # Pokud nebyly nalezeny strany, ale HTML existuje, může to být problém
             print(f"Varování: Pro obec {obec.name} nebyly nalezeny žádné výsledky stran, ačkoliv HTML bylo staženo.")
        vsechny_vysledky.extend(vysledky_stran_pro_obec)
    return vsechny_vysledky

def uloz_do_csv(data, filename):
    if not data:
        print("Žádná data k uložení.")
        return

    print(f"Připravuji data pro uložení do souboru: {filename}")
    
    party_names = sorted(list(set(vysledek.strana.name for vysledek in data)))
    summary_stat_keys = ['registered', 'envelopes', 'valid']
    
    obce_data_restructured = {}
    for vysledek in data:
        obec_obj = vysledek.obec
        obec_key = (obec_obj.kod, obec_obj.name)
        if obec_key not in obce_data_restructured:
            obce_data_restructured[obec_key] = {
                'registered': obec_obj.registered,
                'envelopes': obec_obj.envelopes,
                'valid': obec_obj.valid,
                'party_votes': {} 
            }
        obce_data_restructured[obec_key]['party_votes'][vysledek.strana.name] = vysledek.hlasy

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            header = ['Obec_Kod', 'Obec_Nazev'] + summary_stat_keys + party_names
            writer.writerow(header)
            
            for (kod, nazev), combined_data in obce_data_restructured.items():
                row = [kod, nazev] + \
                    [combined_data.get(key, 0) for key in summary_stat_keys] + \
                    [combined_data['party_votes'].get(party_name, 0) for party_name in party_names]
                writer.writerow(row)
                
        print(f"Data byla úspěšně uložena do {filename}")
    except IOError as e:
        print(f"Chyba při zápisu do souboru {filename}: {e}")


def main():
    if len(sys.argv) != 3:
        print("Chyba: Skript vyžaduje 2 argumenty: URL a název výstupního CSV souboru.")
        print("Příklad: python scraper.py \"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103\" vysledky_prostejov.csv")
        sys.exit(1)

    url_argument = sys.argv[1]
    csv_filename_argument = sys.argv[2]

    print(f"Spouštím scrapování pro URL: {url_argument}")
    print(f"Výstupní soubor: {csv_filename_argument}")

    all_obce_objects = ziskej_informace_o_obcich(url_argument)
    
    if all_obce_objects:
        final_results = zpracuj_vsechny_url_obci(all_obce_objects)
        if final_results:
            uloz_do_csv(final_results, csv_filename_argument)
        else:
            print("Nebyla získána žádná data o výsledcích stran k uložení.")
    else:
        print("Nebyly vytvořeny žádné objekty obcí, nebo se nepodařilo extrahovat data.")

if __name__ == '__main__':
    main()
