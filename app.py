#coding:utf8
import sys
import os
import pandas as pd
import sqlite3
import requests
from time import sleep
from bs4 import BeautifulSoup



def clean_adresse(adresse):
    """Formattage des adresses"""
    r = requests.get('https://api-adresse.data.gouv.fr/search/?q=%s' % adresse)
    if r.ok:
        if len(r.json()['features']):
            return r.json()['features'][0]['properties']['label'].replace('’', "'").replace('œ', 'oe')
    else:
        return adresse


def inpi_search(adresse):
    """Requète à l'inpi pour identifier un franchisé"""

    #Données de connexion
    # cookies = {
    #     'Q71x4Drzmg@@': 'v1Vbwwgw@@aqess',
    #     'cookieconsent_status': 'allow',
    #     'PHPSESSID': 'efe4gs3jdg7md0snilludui66oss',
    # }
    print(adresse)
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'Content-Type': 'text/plain;charset=UTF-8',
        'Accept': '*/*',
        'Origin': 'https://data.inpi.fr',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        }

    data = '{"query":{"type":"companies","selectedIds":[],"sort":"relevance","order":"asc","nbResultsPerPage":"5","page":"1","filter":{},"q":"","advancedSearch":{"checkboxes":{"status":{"searchField":["is_rad"],"values":[{"value":"false","checked":true},{"value":"true","checked":true}]}},"texts":{"address":{"searchField":["idt_physical_person.adr_siege_1.folding","idt_physical_person.adr_siege_2.folding","idt_physical_person.adr_siege_3.folding","idt_physical_person.adr_siege_ville.folding","idt_adr_siege_full.folding","etablissements.adr_ets_1.folding","etablissements.adr_ets_2.folding","etablissements.adr_ets_3.folding","etablissements.adr_ets_ville.folding"],"value":"%s"}},"multipleSelects":{},"dates":{}},"searchType":"advanced"},"aggregations":["idt_cp_short","idt_pm_code_form_jur"]}'%adresse
    response = requests.post('https://data.inpi.fr/search', headers=headers, data=data)
    if response.ok:
        from pprint import pprint
        ret = response.json()
        try:
            return ret['result']['hits']['hits'][0]['_source']['siren']
        except:

            pprint('Pas de résultat')
            return ''


def company_ninja(siren):
    if siren:
        r = requests.get(f"https://societe.ninja/data.php?siren={siren}")
        if r.ok:
            try:
                soup = BeautifulSoup(r.content, 'html.parser')
                tab = soup.find('table', attrs={'id': 'menu_representants'})

                dirigeant = soup.select_one('#menu_representants > tbody > tr > td:nth-child(3)').contents[0].strip()
                print(dirigeant)
                return dirigeant
            except Exception as e:
                print(e)
                return ''
    else:
        return ''


def main(db_name, seed):
    print(1)
    conn = sqlite3.connect(db_name)
    s = pd.read_csv(seed)
    s.to_sql(db_name, conn, if_exists='replace', index=False)
    cur = conn.cursor()
    cur.execute('pragma encoding')

    df = pd.read_sql_query("select * from %s" %db_name, conn)
    print(2)
    for index, row in df.iterrows():
        print(3.1)
        row['adresse'] = clean_adresse(row['adresse'])
        print(3.2)
        cur.execute(f"UPDATE {db_name} SET '%s' = ? WHERE id = ?" % 'adresse', (row['adresse'], row['id']))
        print(3.3)
        row['siren'] = inpi_search(row['adresse'])
        print(3.4)
        cur.execute(f"UPDATE {db_name} SET '%s' = ? WHERE id = ?" % 'siren', (row['siren'], row['id']))
        cur.execute(f"UPDATE {db_name} SET '%s' = ? WHERE id = ?" % 'franchise', ('yes', row['id']))
        if row['siren']:
            row['gerant'] = company_ninja(row['siren'])
            cur.execute(f"UPDATE {db_name} SET '%s' = ? WHERE id = ?" % 'gerant', (row['gerant'], row['id']))
            cur.execute(f"UPDATE {db_name} SET '%s' = ? WHERE id = ?" % 'done', ('yes', row['id']))
        sleep(0.5)
    return

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("python app.py {{nom de l'enseigne}} {{chemin du fichier csv}}")
        exit()
    db_name = sys.argv[1]
    if not 'csv' in sys.argv[2] or not os.path.isfile(sys.argv[2]):
        print("Le deuxième argument doit être un fichier csv valide")
        exit()
    seed = sys.argv[2]
    main(db_name, seed)
