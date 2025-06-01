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
    obce_data_dict = ziskej_obecna_data(url) # Přejmenoval jsem 'dict' na 'obce_data_dict' pro jasnost
    
    # --- NOVĚ PŘIDANÝ SEZNAM PRO ULOŽENÍ OBJEKTŮ OBCE ---
    list_of_obec_objects = [] 
    # ----------------------------------------------------

    # Kontrola, zda ziskej_obecna_data vrátila platná data (není False)
    if obce_data_dict:
        # Řádek 49: Původní loop začínal zde. Nahraďte následujícími řádky:
        for cislo_key, (jmeno, kod) in obce_data_dict.items():
            # Sestavíme specifické URL pro detailní stránku obce.
            # Zde používáme globální konstanty definované výše.
            obec_detail_url = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={URL_KRAJ_PARAM}&xobec={kod}&xvyber={URL_VYBER_PARAM}"
            
            # Vytvoříme objekt třídy Obce s jménem, kódem a detailní URL
            current_obec_obj = Obce(name=jmeno, kod=kod, url=obec_detail_url)
            
            # Přidáme vytvořený objekt do seznamu
            list_of_obec_objects.append(current_obec_obj)
            
            # Volitelné: Pro ověření tiskneme vytvořený objekt
            print(f"Vytvořen objekt: Jméno='{current_obec_obj.name}', Kód='{current_obec_obj.kod}', URL='{current_obec_obj.url}'")
        
        # Funkce nyní vrací seznam objektů Obce
        return list_of_obec_objects
    else:
        print("Nelze vytvořit objekty Obce, protože ziskej_obecna_data vrátila chybu.")
        return False
def main():
    # Zde původně bylo 'dict = ziskej_info(URL)', nyní získáme seznam objektů
    all_obce_objects = ziskej_info(URL)
    
    if all_obce_objects:
        print("\n--- Zde jsou všechny vytvořené objekty Obce ---")
        for obec_obj in all_obce_objects:
            # Nyní můžete přistupovat k atributům každého objektu
            print(f"Objekt: {obec_obj.name}, Kód: {obec_obj.kod}, Detail URL: {obec_obj.url}")
            # Zde byste pak volali metodu jako obec_obj.getdata() (pokud ji implementujete)
            # k načtení dalších dat a jejich uložení do atributů objektu.
    else:
        print("Nebyly vytvořeny žádné objekty obcí.")
main()


        
