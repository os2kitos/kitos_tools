import json
import os
import pathlib
import string
import uuid

import click

import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

from xml.dom.minidom import parse, parseString

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

SETTINGS = json.loads(cfg_file.read_text())


class ArchimateHelper:
    def __init__(self, archifile):
        self.archifile = archifile
        self.archi_dom = parse(self.archifile)

        self.application_folder = None

        folder_elements = self.archi_dom.getElementsByTagName('folder')

        for folder in folder_elements:
            if folder.getAttribute('type') == 'application':
                self.application_folder = folder
                break

    def save(self):
        writer = open(self.archifile, encoding='utf-8', mode='w')
        self.archi_dom.writexml(writer)
        writer.close()

    def create_application_folder(self, folder_name):
        newFolder = self.archi_dom.createElement("folder")
        newFolder.setAttribute("name", folder_name)
        newFolder.setAttribute("id", self._make_guid())
        return newFolder

    def _make_guid(self):
        return str(uuid.uuid4())

    def update_storm_structure(self):
        for storm_category, storm_classes in SETTINGS['archimate.STORM'].items():
            app_node = self.get_named_application_folder(storm_category)
            if app_node == None:
                app_node = self.create_application_folder(storm_category)
                self.application_folder.appendChild(app_node)

            for storm_class in storm_classes:
                sub_app_node = self.get_named_application_folder(
                    storm_class)
                if sub_app_node == None:
                    sub_app_node = self.create_application_folder(
                        storm_class)
                    app_node.appendChild(sub_app_node)

    def get_named_application_folder(self, folder_name):
        return self._find_childnode_from_attributes(self.application_folder, "folder", {"name": folder_name})

    def _find_childnode_from_attributes(self, dom_node, element_name, attributes):
        child_nodes = dom_node.getElementsByTagName(element_name)
        child_node = None
        for child in child_nodes:
            if self.has_named_attributes(child, attributes):
                child_node = child
                break

        return child_node

    def _get_named_attribute(self, element, attribute_name):
        return element.getAttributeNode(attribute_name)

    def has_named_attributes(self, dom_node, attributes):
        found = False
        found_count = 0

        for attr_name, attr_value in attributes.items():
            if attr_value == dom_node.getAttribute(attr_name):
                found_count += 1

        if found_count == len(attributes):
            found = True

        return found


@click.command()
@click.option('--archifile', help='archimate file')
def update_archimate_model(archifile):
    ah = ArchimateHelper(archifile)
    ah.update_storm_structure()
    ah.save()


if __name__ == '__main__':
    kl.start_logging("archimate_sync.log")
    update_archimate_model()
