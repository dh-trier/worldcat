#!/usr/bin/env python3

"""
Script for creating a minimal metadata table of a collection of novels.
The table contains the novel id, title and name of the author.

Input: xml files (novels)
Output: metadata as csv-file
"""


from bs4 import BeautifulSoup as bs
import os
from os.path import join
import glob
import re
import pandas as pd



# === Functions ===

def read_xml(file):
    """
    Parsing with Beautiful Soup, see: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    
    input: xml file
    output: parsed xml
    
    """
    with open(file, "r", encoding="utf8") as infile: 
        xml = infile.read()
        xml = bs(xml, "xml")
        return xml


def get_id(file):
    """
    Extracts the xml:id from the xml file.
    """
    with open(file, "r", encoding="utf8") as infile: 
        text = infile.read()
        id = re.search("xml:id=\"(.*?)\"", text).group()
        id = re.search("\"(.*?)\"", id).group()
        id = re.sub("\"", "", id)
    
    basename,ext = os.path.basename(file).split(".")
    print(id)
    return id, basename


def get_title(xml):
    """
    Extracts the title from the teiHeader.
    """
    title = xml.find("title").get_text()
    return title


def get_author(xml):
    """
    Extracts the author name from the teiHeader.
    """
    author = xml.find("author").get_text()
    author = re.sub('\((.*?)\)', "", author)
    return author


def append_dict(dict, id, basename, title, author):
    """
    Adds metadata to the dictionary.
    """
    dict[id] = [basename, title, author]
    return dict


def save_csv(dict, settings_dict):
    """
    Turns the dictionary into a dataframe.
    Saves the dataframe to a csv file.
    """
    dataframe = pd.DataFrame.from_dict(dict, orient="index")
    dataframe.to_csv('{}_metadata.csv'.format(settings_dict["lang"]), index_label="xmlid", header = ["basename", "title", "au-name"], sep="\t")
    
    
# === Coordinating function ===

def main(settings_dict):
    """
    Coordinates the creation of the metadata table.
    """
    print("--getmetadata")
    dict = {}
    
    xmlfolder = settings_dict["xml_path"]
    for file in glob.glob(xmlfolder):
        xml = read_xml(file)
        id, basename = get_id(file)
        title = get_title(xml)
        author = get_author(xml)
        append_dict(dict, id, basename, title, author)
        save_csv(dict, settings_dict)
