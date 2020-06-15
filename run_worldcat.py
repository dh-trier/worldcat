

# Imports and parameters

import yaml 
import get_settings
import get_metadata 
import get_htmlworldcat
import create_publicationtable
import create_summary

configfile = "config.yaml"


def main(configfile): 
    with open(configfile, 'r') as configfile:
        config = yaml.safe_load(configfile)
        settings_dict = get_settings.main(config["lang"], config["basedir"], config["level"], config["write_file"], config["htmlpages"])
        get_metadata.main(settings_dict)
        get_htmlworldcat.main(settings_dict)
        create_publicationtable.main(settings_dict)
        create_summary.main(settings_dict)
    

main(configfile)
