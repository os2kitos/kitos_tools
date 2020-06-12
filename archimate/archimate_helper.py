import codecs
import json
import logging
import os
import pathlib
import string
import uuid
from xml.dom.minidom import parse, parseString

logger = logging.getLogger("archimate-helper")

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')


SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))


class ArchimateHelper:
    def __init__(self, archifile, outfile):
        self.archifile = archifile
        self.outfile = outfile
        self.archi_dom = parse(self.archifile)
        self.replaced_ids = {}

        self.application_folder = None
        self.relations_folder = None

        folder_elements = self.archi_dom.getElementsByTagName('folder')

        for folder in folder_elements:
            if folder.getAttribute('type') == 'application':
                self.application_folder = folder

            if folder.getAttribute('type') == 'relations':
                self.relations_folder = folder

            if self.relations_folder is not None and self.application_folder is not None:
                break

    def save(self, strip_empty_lines=True):

        temp_file = f"{self.outfile}.temp"

        writer = open(temp_file, encoding='utf-8', mode='w')
        self.archi_dom.writexml(writer, indent="\t", addindent="\t", newl="\n")
        writer.close()

        replace = True if len(self.replaced_ids) > 0 else False

        if strip_empty_lines or replace:
            with open(temp_file, encoding='utf-8', mode='r') as infile, open(self.outfile, encoding='utf-8', mode='w') as outfile:
                for line in infile:
                    if not line.strip():
                        continue  # skip the empty line
                    if replace:
                        for cur_id, new_id in self.replaced_ids.items():
                            line = line.replace(cur_id, new_id)
                    outfile.write(line)  # non-empty line. Write it to output

            outfile.close()
            infile.close()

        os.remove(temp_file)

    def create_application_folder(self, folder_name, id=None):
        if id == None:
            id = self._make_guid()

        newFolder = self.archi_dom.createElement("folder")
        newFolder.setAttribute("name", folder_name)
        newFolder.setAttribute("id", id)
        return newFolder

    def create_application_element(self, application_name, application_id=None):
        if application_id == None:
            application_id = self._make_guid()

        newElement = self.archi_dom.createElement("element")
        newElement.setAttribute("xsi:type", "archimate:ApplicationComponent")
        newElement.setAttribute("name", application_name)
        newElement.setAttribute("id", application_id)
        return newElement

    def update_application_id(self, element_node, application_id):
        # read current id from element_node and assign new ID
        # read entire XML file, search and replace style, for references
        # to old id and replace them with the new.
        current_id = element_node.getAttribute("id")
        element_node.setAttribute("id", application_id)
        self.replaced_ids.update({current_id: application_id})

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

    def update_application_relations(self, relations):
        # find relations folder
        for index in range(len(relations)):
            relation = relations[index]
            # re-use kitos relation uuid when inserting
            relation_id = relation["uuid"]

            # ystem source id
            source_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
                str(relation["fromUsage"]["id"])
            target_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
                str(relation["toUsage"]["id"])

            rel_node = self._find_childnode_from_attributes(
                self.relations_folder, "element", {"id": relation_id})

            if rel_node is not None:
                print("Found node!")
            else:
                print(
                    f"new relation with source: {source_id} and target: {target_id} must be created")

    def get_named_application_folder(self, folder_name):
        return self._find_childnode_from_attributes(self.application_folder, "folder", {"name": folder_name})

    def get_application_element_from_name(self, application_name):
        return self._find_childnode_from_attributes(self.application_folder, "element", {"name": application_name, "xsi:type": "archimate:ApplicationComponent"})

    def get_application_element_from_id(self, application_id):
        return self._find_childnode_from_attributes(self.application_folder, "element", {"id": application_id, "xsi:type": "archimate:ApplicationComponent"})

    def move_application(self, app_node, new_parent_node):
        """
        //Clone existing node with all child nodes
        $newEl = $applicationNode->cloneNode(true);
        //Move to the current categoryNode
        $newParentNode->appendChild($newEl);
        //Delete existing node
        $oldEl = $oldParentNode->removeChild($applicationNode);
        return $newEl; 
        """
        new_element = app_node.cloneNode(True)
        new_parent_node.appendChild(new_element)

        parent_node = app_node.parentNode
        parent_node.removeChild(app_node)
        app_node.unlink()

        return new_element

    def _find_childnode_from_attributes(self, dom_node, element_name, attributes):
        child_nodes = dom_node.getElementsByTagName(element_name)
        child_node = None
        for child in child_nodes:
            if self.has_named_attributes(child, attributes):
                child_node = child
                break

        return child_node

    def has_named_attributes(self, dom_node, attributes):
        found = False
        found_count = 0

        for attr_name, attr_value in attributes.items():
            if dom_node.hasAttribute(attr_name) and attr_value == dom_node.getAttributeNode(attr_name).value:
                found_count += 1

        if found_count == len(attributes):
            found = True

        return found
