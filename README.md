# Scraper volebních výsledků z Volby.cz

Tento Python skript (`scraper.py`) slouží k automatizovanému stahování a zpracování výsledků parlamentních voleb v České republice z webových stránek `www.volby.cz`. Umožňuje uživateli specifikovat konkrétní územní celek prostřednictvím URL adresy a název výstupního souboru, do kterého se uloží sesbíraná data ve formátu CSV.

## Popis

Skript prochází zadanou URL, identifikuje jednotlivé obce v daném územním celku, a pro každou obec stahuje detailní stránku s volebními výsledky. Z těchto stránek extrahuje:
*   Souhrnné statistiky účasti (počet voličů v seznamu, vydané obálky, platné hlasy).
*   Počty hlasů pro jednotlivé politické strany.

Všechna data jsou následně agregována a uložena do CSV souboru v přehledném formátu.

## Funkce

*   **Získání seznamu obcí:** Načte kódy a názvy obcí z hlavní stránky územního celku.
*   **Extrakce parametrů z URL:** Automaticky získá parametry `xkraj` a `xnumnuts` (odpovídající `xvyber`) z uživatelem zadané URL pro správné sestavení odkazů na detaily obcí.
*   **Parsování detailních výsledků:** Pro každou obec extrahuje souhrnné statistiky a hlasy pro politické strany pomocí regulárních výrazů.
*   **Ukládání do CSV:** Uloží všechna data do jednoho CSV souboru, kde každý řádek reprezentuje jednu obec a sloupce obsahují identifikační údaje obce, souhrnné statistiky a počty hlasů pro každou stranu.

## návod 
Požadavky:
*   Python 3.x
*   Knihovny (instalovatelné přes pip):)

Klonování repozitáře:
```bash
git clone https://github.com/KR3915/PS2017-scrape 
```
navigace do repozitáře:
```bash
cd PS2017-scrape
```
Instalace `knihoven`:
```bash
pip install -r requirements.txt
```
Instalace `knihoven`:
```bash
pip install -r requirements.txt
```
### Spuštění
script je potřeba předat s dvěma argumenty první je adresa kterou chceme scrapovat, druhá je název souboru do kterého chceme ukládat zde je ukázka pro 
`windows`
```bash
python scraper.py "adresa" "example.csv"
```
Spouštení `Linux/MacOS`
```bash
py scraper.py "adresa" "example.csv"
```
