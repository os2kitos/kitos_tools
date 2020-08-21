import os
import json
import pathlib
import click
import logging


import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

import archimate_helper as ah

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

logger = logging.getLogger("kitos-archimate")


SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))


@click.command()
@click.option('--infile', help='archimate file')
@click.option('--outfile', help='archimate file')
@click.option('--name', 'search_type', flag_value='name', help='Use IT system name as key. This also updates IDs')
@click.option('--id', 'search_type', flag_value='id', help='Use IT system ID as key')
def update_archimate_model(infile, outfile, search_type):
    archi_helper = ah.ArchimateHelper(infile, outfile)
    archi_helper.update_storm_structure()

    kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                     SETTINGS['KITOS_URL'], False, False)

    #sys_file = pathlib.Path.cwd() / 'itsystems.json'
    #it_systems = json.loads(sys_file.read_text(encoding='utf-8'))

    # import and/or update applications
    it_systems = kh.return_itsystems()
    archi_helper.update_applications(search_type, it_systems)

    # import and/or update relations
    relations = kh.return_itsystem_relations()
    archi_helper.update_application_relations(relations)

    archi_helper.save()


def save_itsystems():
    kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                     SETTINGS['KITOS_URL'], False, False)
    it_systems = kh.return_itsystems()

    with open("itsystems.json", encoding='utf-8', mode='w') as outfile:
        json.dump(it_systems, outfile)


def test_relations():
    archi_helper = ah.ArchimateHelper(
        "test_in.archimate", "test_out.archimate")
    archi_helper.update_storm_structure()

    kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                     SETTINGS['KITOS_URL'], False, False)

    relations = kh.return_itsystem_relations()

    archi_helper.update_application_relations(relations)
    archi_helper.save()


if __name__ == '__main__':
    kl.start_logging("archimate_sync.log")
    update_archimate_model()
    # save_itsystems()
    # test_relations()
