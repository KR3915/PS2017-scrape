import requests
import re
################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
###################################
URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103"
CSV = "volebni_data.csv"
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
    def getdata(url):
        pass

class strana:
    def __init__(self, name, hlasy ):
        self.name = name
        self.hlasy = hlasy

class vysledkystrany:
    def __init__(self, obec, strana, hlasy):
        self.obec = obec
        self.strana = strana
        self.hlasy = hlasy

def ziskej_obecna_data(url):
    r = requests.get(url)
    list_cisel = []
    html = r.text
    list_jmen = re.findall(patterns["obce_jmeno"], html)
    list_kodu = re.findall(patterns["obec_kod"], html)
    if len(list_jmen) == len(list_kodu):
        print(f"jmena {list_jmen}\n -------------------------------------------------------- \n {list_kodu} ")
        for i in range(len(list_jmen)):
            list_cisel.append(str(i))
        obce_list = list(zip(list_jmen, list_kodu))
        obce_dict = dict(zip(list_cisel, obce_list))
        print(obce_dict)
        return obce_dict

def ziskej_info(url):
    obce_data_dict = ziskej_obecna_data(url)

    list_of_obec_objects = [] 
    if obce_data_dict:
        for cislo_key, (jmeno, kod) in obce_data_dict.items():
            obec_detail_url = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={URL_KRAJ_PARAM}&xobec={kod}&xvyber={URL_VYBER_PARAM}"
            current_obec_obj = Obce(name=jmeno, kod=kod, url=obec_detail_url)
            list_of_obec_objects.append(current_obec_obj)
            print(f"Vytvořen objekt: Jméno='{current_obec_obj.name}', Kód='{current_obec_obj.kod}', URL='{current_obec_obj.url}'")
        return list_of_obec_objects
    else:
        print("Nelze vytvořit objekty Obce, protože ziskej_obecna_data vrátila chybu.")
        return False

def main():
    all_obce_objects = ziskej_info(URL)
    
    if all_obce_objects:
        print("\n--- Zde jsou všechny vytvořené objekty Obce ---")
        for obec_obj in all_obce_objects:
            print(f"Objekt: {obec_obj.name}, Kód: {obec_obj.kod}, Detail URL: {obec_obj.url}")
    else:
        print("Nebyly vytvořeny žádné objekty obcí.")
main()


        
