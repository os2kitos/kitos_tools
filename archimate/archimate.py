import os
import json
import pathlib
import click


import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

import archimate_helper as ah

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')


SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))


@click.command()
@click.option('--infile', help='archimate file')
@click.option('--outfile', help='archimate file')
def update_archimate_model(infile, outfile):
    archi_helper = ah.ArchimateHelper(infile, outfile)
    archi_helper.update_storm_structure()

    app_node = archi_helper.get_named_application_element("ITAL TEST")

    cat_node = archi_helper.get_named_application_folder(
        SETTINGS['archimate.STORM']["Web og kommunikation"][3])

    if app_node == None:
        new_element = archi_helper.create_application_element("ITAL TEST")
        cat_node.appendChild(new_element)

    app_node1 = archi_helper.get_named_application_element(
        "Det Digitale Vandløbsregulativ (DVR)")
    if app_node1 != None:
        print(app_node1)

    app_node = archi_helper.get_named_application_element("ITAL TEST")
    archi_helper.update_application_id(app_node, "my_custom_id")

    archi_helper.save(True)


if __name__ == '__main__':
    kl.start_logging("archimate_sync.log")
    update_archimate_model()
