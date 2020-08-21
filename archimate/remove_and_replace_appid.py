"""
This script can be used to "merge" to applications in archimate model
--infile: input archimate file 
--outfile: output archimate file
--newid: the app id that will replace "replacedid"
--replacedid: the app id to be replaced.

All references in model for "replacedid" will be replaces by "id"
"""


import os
import json
import pathlib
import click
import logging


import kitos_helper.kitos_logger as kl

import archimate_helper as ah

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

logger = logging.getLogger("kitos-archimate")


SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))


@click.command()
@click.option('--infile', help='archimate file')
@click.option('--outfile', help='archimate file')
@click.option('--replacedid', help='ID to remove and replace')
@click.option('--newid', help='ID to replace with')
def replace_ids(infile, outfile, replacedid, newid):
    archi_helper = ah.ArchimateHelper(infile, outfile)
    archi_helper.remove_and_replace_application(replacedid, newid)
    archi_helper.save()


if __name__ == '__main__':
    kl.start_logging("remove_and_replace.log")
    replace_ids()
