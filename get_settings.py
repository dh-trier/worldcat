# This  script will apply all settings, which are chosen in config.yaml
# It includes: the language, based on that the xml-folder, the csv-file, the language-parameter for the worldcat-url, the write-file, which stores the
# html-pages, and the htmlpages parameter
# the data is stored in a dictionary, that will be used in the run_worldcat.py (and the dependent scripts)
import os
from os.path import join

def get_lang(lang, d): # input: empty dictionary, the chosen language; new key "lang", value is the chosen language  
    
    d["lang"] = lang
    
    return lang, d
    
    
def get_xml_folder(d, basedir, level): # input: dictionary, xml_path, level (both parameters from config.yaml); gets to the chosen language and the chosen level
    
    #print(level)
    if not os.path.isdir(basedir):   # checking the xmlpath
        print("Wrong path. No XML-TEI files can be found. Please adjust the basedir variable in the config file!")
    xml_folder = basedir + "/ELTeC-{}/{}/*.xml".format(d["lang"], level)
    d["xml_path"] = xml_folder
    
    return d, xml_folder

def get_csv_file(d): # input: dictionary; returns csv_file with language extention
    
    csv_file = d["lang"] + "_" + "metadata.csv"
    d["csv_file"] = csv_file
    
    return d

def get_lang_worldcat(lang, d): # matches the chosen language to the language-code in worldcat
    
    worldcat_lang = {"fra": "fre", "eng":"eng", "ita":"ita", "deu":"ger", "por":"por", "spa":"spa", "srp":"srp", "gre":"gre", "hun":"hun", "slv":"slv", "rom":"rum", "nor":"nor", "cze":"cze"} # dictionary contains ELTeC-language abbreviations as keys, worldcat-language codes as values 
    #print("lang", lang)
    for key, value in worldcat_lang.items():
        
        if lang == key:
            lang_worldcat = value
            break
        else:
            print("choose valid lang")
    
    d["lang_worldcat"] = lang_worldcat # creates new dictionary key 
    return lang, d

def get_lang_hit(lang, d):  # matches the chosen language to the language category in worldcat
    
    hit_lang = {"fra":"French", "eng":"English", "ita":"Italian" , "deu":"German", "por":"Poruguese", "spa":"Spanish", "srp":"Serbian", "gre":"Greek, Modern[1453-]", "hun":"Hungarian", "slv":"Slovenian", "rom":"Romanian", "nor":"Norwegian", "cze":"Czech"} # dictionary contains ELTeC-language abbreviations as keys, worldcat-language category as values
    for key, value in hit_lang.items():
        
        if lang == key:
            lang_hit = value
            break
        else:
            print("choose valid lang")
    
    d["lang_hit"] = lang_hit
    return d

def get_write_file(d, write_file): # for creating or using a sub-file for each language, where html-pages will be stored
    
    new_write_file = join(write_file, d["lang"])
    #print("new write file", new_write_file)
    
    d["write_file"] = new_write_file
    return new_write_file, d

def get_html_file(d, htmlpages): # will be used to get the right html pages, based on the htmlpages-parameter of the config.yaml
    
    html_folder, ext = htmlpages.split("/")
    html_folder = join(html_folder, d["lang"], ext)
    #print("html_folder",html_folder)
    #print("ext", ext)
    d["html_folder"] = html_folder

    return html_folder, d
    
def main(lang, basedir, level, write_file, htmlpages):
    print("--getsettings")
    d = {}
    lang, d = get_lang(lang, d)
    d, xml_folder = get_xml_folder(d, basedir, level)
    d = get_csv_file(d)
    lang, d =  get_lang_worldcat(lang, d)
    d = get_lang_hit(lang, d)
    new_write_file, d = get_write_file(d, write_file)
    html_folder, d = get_html_file(d, htmlpages) 
    #print(d)
    return d
