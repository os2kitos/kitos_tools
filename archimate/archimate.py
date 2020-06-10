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
    # it_systems = kh.return_itsystems()
    sys_file = pathlib.Path.cwd() / 'itsystems.json'
    it_systems = json.loads(sys_file.read_text(encoding='utf-8'))

    default_category = archi_helper.get_named_application_folder(
        SETTINGS["archimate.DEFAULT_CATEGORY"])

    logger.info(f"Search type: {search_type}")

    for sys_id, it_system in it_systems.items():
        category_name = it_system['Storm navn'].replace(
            "(STORM)", "").strip() if it_system['Storm navn'] != None else SETTINGS["archimate.DEFAULT_KLASSIFIKATION"]

        cat_node = archi_helper.get_named_application_folder(category_name)
        if cat_node == None:
            # Create new category and put it under the default category
            cat_id = SETTINGS["archimate.CATEGORY_ID_PREFIX"] + \
                str(it_system['Storm ID'])
            cat_node = archi_helper.create_application_folder(
                category_name, cat_id)
            default_category.appendChild(cat_node)
            logger.info(f"New STORM classification created: {category_name}")

        app_node = None
        app_sys_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
            str(sys_id)

        if search_type == 'name':
            logger.info(f"Search for system name: {it_system['Systemnavn']}")
            app_node = archi_helper.get_application_element_from_name(
                it_system['Systemnavn'])
        elif search_type == 'id':
            logger.info(f"Search for system id: {app_sys_id}")
            app_node = archi_helper.get_application_element_from_id(
                app_sys_id)

        if app_node == None:
            app_node = archi_helper.create_application_element(
                it_system['Systemnavn'], app_sys_id)
            cat_node.appendChild(app_node)
            logger.info(
                f"Application {it_system['Systemnavn']} with id {app_sys_id} created.")

        if app_node.getAttribute('id') != app_sys_id:
            logger.info(
                f"Updating systemid for {it_system['Systemnavn']}. Old id: {app_node.getAttribute('id')}, new id: {app_sys_id}")
            archi_helper.update_application_id(app_node, app_sys_id)

    archi_helper.save()


def save_itsystems():
    kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                     SETTINGS['KITOS_URL'], False, False)
    it_systems = kh.return_itsystems()

    with open("itsystems.json", encoding='utf-8', mode='w') as outfile:
        json.dump(it_systems, outfile)


if __name__ == '__main__':
    kl.start_logging("archimate_sync.log")
    update_archimate_model()
    # save_itsystems()
