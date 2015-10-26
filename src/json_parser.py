#!/usr/bin/env python

# #####################

import json
import sys

# #####################

from termcolor import cprint
import os


# #####################

class MangaJsonParser:

    # Load configuration from JSON
    def parse_config(self, path):
        cprint("Parsing JSON File...", 'white', attrs=['bold'], file=sys.stdout)
        with open(path) as data:
            configuration = json.load(data)

        return configuration

    # Save configuration to JSON backing up the old one to guarantee integrity
    def save_config(self, path, configuration):
        # Backs up file
        backup_file_name = path + "_bak"
        os.rename(path, backup_file_name)

        with open(path, 'w') as outfile:
            json.dump(configuration, outfile, indent=4, sort_keys=True)

        # The file was succesfully saved and now remove backup
        os.remove(backup_file_name)

