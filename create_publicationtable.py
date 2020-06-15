#!/usr/bin/env python3

"""
Script for creating a table with the number of publications per year for each novel in the collection.

Input: html files from worldcat downloaded by gethtmlsworldcat.py.
Output: csv-file
"""

from bs4 import BeautifulSoup as bs
import glob
import os
from os.path import join
import re
import pandas as pd
import logging

# === Parameters ===

#dir=""
#htmlpages = join(dir, "html", "*.html")


# === Functions ===

def read_html(file):
    """
    Parsing with Beautiful Soup, see: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    
    input: html file
    output: parsed html
    
    """
    with open(file, "r", encoding="utf8") as infile:
        html = infile.read()
        html = bs(html, "html.parser")
        return html


def get_id(file):
    """
    input: file
    output: filename (in this case the id of the novel)
    """
    base = os.path.basename(file)                   
    id_ext = str(os.path.splitext(base)[0])
    id = id_ext.split("_html")[0]
    print(id)
    return id, id_ext


def test_search_result(html, id):
    """
    Prints warning if there are no search results in worldcat and writes warning into log file.
    The warning contains the id and the search strings of the title and the author.
    
    input: html file
    output: log file
    """
    text = "No results match your search"
    try:
        errors = html.find('div', {'class' : 'error-results'}).get_text()
        errors = errors.strip()
        search_string = re.search("ti:(.*?)au:(.*?)\'", errors).group()
        title = re.sub(" au:(.*?)\'", "", search_string)                   # extracts search string for the title
        title = re.sub("ti:", "", title)
        title = re.sub(": ELTeC edition", "", title)
        author = re.search("au:(.*?)\'", search_string).group()            # extracts search string for the author
        author = re.sub("au:", "", author)
        author = re.sub("\'", "", author)
        if errors.startswith(text):
            print(id + ": No search result in worldcat! Please check the spelling of author and title (see log file)!")
            logging.warning(id + ": No search result in worldcat! Search strings: title: '" + title + "', author: '" + author + "'")
    except:
        pass
    

def create_df_worldcat(html, settings_dict, id_ext):
    """
    Takes a html file containing the search result in worldcat and creates a dataframe with hit number (corresponding to the html), hit language and publication year
    If there isn't mentioned a year, it will be set to 0 in order to contribute to the total number of publications. 
    
    input: html file, settings_dict, id
    output: dataframe
    """
    df_worldcat = pd.DataFrame(columns=['number', 'itemLanguage', 'year'])
    list = html.find_all('tr', {'class' : 'menuElem'})               # list with all hits (still marked up)
    
    for item in list:
        number = item.find('div', {'class' : 'item_number'}).get_text()
        itemLang = item.find('span', {'class' : 'itemLanguage'}).get_text()
        try:
            year = item.find('span', {'class' : 'itemPublisher'}).get_text()
            year = re.search("[0-9]+", year).group()   
        except:
            year = "0"
            print("No publication year found for item " + number + " in file " + str(id_ext))
            logging.warning(str(id_ext) + ": No publication year found for item " + number + "!")
        df_worldcat = df_worldcat.append({'number': number, 'itemLanguage': itemLang, 'year': year}, ignore_index=True)
        #print(df_worldcat)
        
    return(df_worldcat)
       

def test_lang(df_worldcat, settings_dict):
    """
    Tests the language of each hit in html. If the language isn't the expected one, the number is stored in a list called skip.
    
    input: html, settings_dict
    output: list with numbers corresponding to hits with "wrong" language.
    
    """
    item_lang = settings_dict["lang_hit"]
    skip = []
    for index, row in df_worldcat.iterrows():
        if row['itemLanguage'] == item_lang:
            pass
        else:
            skip.append(row['number'])         # hit number is appended to skip list if language isn't the expected one
    #print(skip)
    return skip


def fill_publicationlist(df_worldcat, publist, skip):
    """
    
    Adds the publication years of hits with the "right" language to a list.
    If the extracted number hasn't got a value between 1840 an 2019, the year will be set to 0 in order to contribute to the total number of publications.
    
    input: dataframe df_worldcat, publist (empty or already filled with publication years from first pages of the search result), skip (list with numbers corresponding to items with "wrong" language)
    output: list with publication years of one novel
    
    """
 
    for index, row in df_worldcat.iterrows():
        if row['number'] not in skip:
            year = row['year']
            year = int(year)
            if year not in range(1840, 2020):                        # if the publication year isn't a number between 1840 and 2020
                year = 0
            publist.append(year)
    return publist
            

def create_dictionary():
    """
    Returns a dictionary with keys from 1840 to 2019, each value is an empty dictionary.
    """
    keys = [0]
    for x in range(1840,2020):                        # creates a list with keys from 1840 to 2019 and 0 (for cases where there is no mentioned publication year)
        keys.append(x)
    
    pubdict = {key: {} for key in keys}               # creates a dictionary with the keys from the list and sets empty dictionaries as values
    return pubdict


def fill_dictionary(pubdict, publist, id):
    """
    Writes the information from the publication list into the dictionary.
    
    input: dictionary with years from 1840 to 1940 as keys and empty dictionaries as values; list with publication years; id of the novel
    output: dictionary in which every year (1840 to 2019) is related to another dictionary containing the novel id (keys) and the number of publications in the specific year (values)
    """
    
    for x in range(1840,2020):                 # adding a new dictionary entry to each key (year): id of the novel (key) and "0" (number of publications; value)
        d = pubdict[x]
        d[id] = 0
        
    d = pubdict[0]                             # adding the dictionary for the year "0" (cases where there is no mentioned year)
    d[id] = 0
    
    for year in publist:                           # for each year in the list the corresponding number of publications is increased by 1
       pubdict[year][id] = pubdict[year][id] + 1     
    
    return pubdict
    

def create_dataframe(pubdict):
    """
    Changes the dictionary into a dataframe using pandas, see: https://pandas.pydata.org/.
    
    input: dictionary
    output: dataframe
    """
    dataframe = pd.DataFrame.from_dict(pubdict, orient='index')
    return dataframe


def add_sum(dataframe):
    """
    Adds the total number of publications of each novel.
    """
    dataframe.loc['Total']= dataframe.sum()


def save_csv(dataframe, lang):
    """
    Saves the dataframe as csv file.
    """
    dataframe.to_csv('{}_reprint_counts.csv'.format(lang))
     
                
# === Coordinating function ===

def main(settings_dict):
    """
    Coordinates the creation of the publication table.
    """
    print("--createpublicationtable")
    htmlpages = settings_dict["html_folder"]
    lang = settings_dict["lang"]
    logging.basicConfig(filename='{}_publicationtable.log'.format(lang),level=logging.WARNING, format='%(asctime)s %(message)s')
    publdict = create_dictionary()
    publist = []
    id_prev = ""
    
    filenames = []
    for file in glob.glob(htmlpages):
        filenames.append(os.path.basename(file))
    filenames.sort()
    for file in filenames:       
        html = read_html(join(settings_dict["write_file"], file))
        id, id_ext = get_id(file)
        df_worldcat = create_df_worldcat(html, settings_dict, id_ext)
        test_search_result(html, id)
        skip = test_lang(df_worldcat, settings_dict)
        if id == id_prev:                                            # html file contains second, third, ... page of the search result
            publist = fill_publicationlist(df_worldcat, publist, skip)        # existing publist is appended
        else:                                                        # html contains the first page of the search result
            publist = []                                             # a new publist is created
            publist = fill_publicationlist(df_worldcat, publist, skip)
        fill_dictionary(publdict, publist, id)
        id_prev = id
    
    dataframe = create_dataframe(publdict)
    add_sum(dataframe)
    save_csv(dataframe, lang)
        
        
#main(dir, htmlpages)
