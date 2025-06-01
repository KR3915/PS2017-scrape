import requests
import re
################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
###################################
URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103"
CSV = "volebni_data.csv"
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
    html = r.text
    list_jmen = re.findall(patterns["obce_jmeno"], html)
    list_kodu = re.findall(patterns["obec_kod"], html)
    if len(list_jmen) == len(list_kodu):
        print(f"jmena {list_jmen}\n -------------------------------------------------------- \n {list_kodu} ")
        obce_dict = dict(zip(list_jmen, list_kodu))
        print (obce_dict)
    else:
        print("too many names or codes!")
        return False
def main():
    ziskej_obecna_data(URL)
main()


        
