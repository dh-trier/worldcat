"""
Script for downloading html-files from worldcat
Input: metadata-table, which was created by getmetadata.py (csv-file)
Output: html-files for each id in the metadata-table

Script zum Download der html-Seiten von worldcat
Die Metadaten-Tabelle wird dabei als Input gegeben
Output sind die entsprechenden html-Seiten zu jedem Werk in der Metadaten-Tabelle

Beispiel-Suchstring, nach erweiterter Suche, Titel, Autor, nur gedruckte Bücher angewählt;
Suche nach Microfiche und E-Book abgewählt;
Sprache Französisch ausgewählt

https://www.worldcat.org/search?q=ti%3ABelle+rivi%C3%A8re+au%3AAimard&dblist=638&fq=+%28x0%3Abook-+OR+%28x0%3Abook+x4%3Aprintbook%29+-%28%28x0%3Abook+x4%3Adigital%29%29+-%28%28x0%3Abook+x4%3Amic%29%29%29+%3E+x0%3Abook+%3E+ln%3Afre&qt=facet_ln%3A

Dieser Suchstring wird als plain_suchstring übergeben; Autor und Titel wurden mit {} für die .format-Methode ersetzt

"""

import requests
import os
from os.path import join
import pandas as pd
import re


def read_csv(csv_file):
    """
    read metadata-table
    Metadaten-Tabelle wird eingelesen
    """
    with open(csv_file, encoding = "utf8") as infile:
        data = pd.read_csv(infile, sep = "\t")
        #print(data.head())
    return data
   
   
def get_author(data):
    """
    get author
    Autoren-Name wird aus Metadaten-Tabelle entnommen
    """
    author = data["au-name"]
    author = author.split(",")[0]
    print(author)
    return author


def get_title(data):
    """
    get title
    Titel wird der Metadaten-Tabelle entnommen
    """
    title = data["title"]
    title = title.split(": ELT")[0]
    print(title)
    return title
    
def generate_suchstring(settings_dict, title, author):
    """
    Die Url wird über .format mit Titel und Autor  modifiziert
    """
    plain_suchstring = "https://www.worldcat.org/search?q=ti%3A{}+au%3A{}&fq=+%28x0%3Abook-+OR+%28x0%3Abook+x4%3Aprintbook%29+-%28%28x0%3Abook+x4%3Adigital%29%29+-%28%28x0%3Abook+x4%3Amic%29%29+-%28%28x0%3Abook+x4%3Abraille%29%29+-%28%28x0%3Abook+x4%3Alargeprint%29%29%29+%3E+ln%3A{}+%3E+ln%3A{}&dblist=638&start={}&qt=page_number_link"
    suchstring = plain_suchstring.format(title, author, settings_dict["lang_worldcat"], settings_dict["lang_worldcat"], 1)
    #print(suchstring)
    return suchstring


def get_html(suchstring, data, write_file, filename_number, lang):
    """
    get html with the requests-library
    Mit requests wird die html heruntergeladen
    """
    #print(suchstring)
    try:
        html = requests.get(suchstring)
        html = html.text
        save_html(data, write_file, html, filename_number, lang)
        #print(html)
        
        start = re.sub("start=1", "start={}", suchstring)
    
        numbers_of_result = re.search("of about <strong>(.*?)</strong>",html).group(1)
        print("Number of results: ", numbers_of_result)

        x = 11
        while x <= int(numbers_of_result):
            try:
                modified_url = start.format(x)
                #print(modified_url)
                modified_url = requests.get(modified_url)
                modified_url = modified_url.text
                filename_number += 1
                save_html(data, write_file, modified_url, filename_number, lang)
                x += 10
            except AttributeError:
                print("Url not found")
        
    except AttributeError:
        print("Url not found")
    return html
    
    
def save_html(data, write_file, html, filename_number, lang):
    """
    Die html-Seiten werden abgespeichert; im Folgenden werden die Dateien mit Autor_Titel_html.html gespeichert
    """
    #with open(join(write_file, "{}_{}_html.html".format(author, title)), "w", encoding="utf8") as outfile:
    #    outfile.write(html)
    
    """
    Besser zur Weiterverarbeitung: filename oder xml-id aus Metadatentabelle:
    """
    if not os.path.exists(write_file): 
        os.makedirs(write_file)
    filename = data["basename"]
    xmlid = data["xmlid"]
    with open(join(write_file, "{}_html{}.html".format(xmlid, filename_number)), "w", encoding="utf8") as outfile:
        outfile.write(html)


def main(settings_dict):
    print("--gethtmlworldcat")
    filename_number = 1
    csv_file = settings_dict["csv_file"]
    write_file = settings_dict["write_file"]
    lang = settings_dict["lang"]
    data = read_csv(csv_file)
    for index, data in data.iterrows():
        print(data["xmlid"])
        author = get_author(data)
        title = get_title(data)
        suchstring = generate_suchstring(settings_dict, title, author)
        html = get_html(suchstring, data, write_file, filename_number, lang)
        #save_html(data, write_file, html, author, title)
    
