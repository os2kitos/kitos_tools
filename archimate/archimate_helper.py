import codecs
import json
import logging
import os
import pathlib
import string
import uuid
from xml.dom.minidom import parse, parseString

logger = logging.getLogger("kitos-archimate")

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

    """[summary]

    Creates new relationsship element ready to be inserted into the Archimate DOM


    <element id="<relation_id>" name="<name>" source="<source_id>" target="<target_id>" xsi:type="archimate:AssociationRelationship">
        <documentation>documentation</documentation>
    </element>
    """

    def create_relation_element(self, relation_id, source_id, target_id, documentation=None):

        newElement = self.archi_dom.createElement("element")
        newElement.setAttribute(
            "xsi:type", "archimate:AssociationRelationship")
        newElement.setAttribute("source", source_id)
        newElement.setAttribute("target", target_id)
        newElement.setAttribute("id", relation_id)
        if documentation is not None:
            doc_element = self.archi_dom.createElement("documentation")
            doc_text = self.archi_dom.createTextNode(documentation)
            doc_element.appendChild(doc_text)
            newElement.appendChild(doc_element)

        return newElement

    def update_application_id(self, element_node, application_id):
        # read current id from element_node and assign new ID
        # read entire XML file, search and replace style, for references
        # to old id and replace them with the new.
        current_id = element_node.getAttribute("id")
        element_node.setAttribute("id", application_id)
        self.replace_application_id(current_id, application_id)

    def replace_application_id(self, current_id, new_id):
        self.replaced_ids.update({current_id: new_id})

    def remove_and_replace_application(self, current_id, new_id):
        remove_app = self.get_application_element_from_id(current_id)
        if remove_app is not None:
            remove_parent = remove_app.parentNode
            remove_parent.removeChild(remove_app)
            remove_app.unlink()
            self.replace_application_id(current_id, new_id)
            logger.info(
                f"Removed {current_id} and added it to replace list to be replaced with {new_id}.")
        else:
            logger.error(
                f"Application element with id: {current_id} does not exist.")

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

    def update_applications(self, search_type, kitos_applications):

        default_category = self.get_named_application_folder(
            SETTINGS["archimate.DEFAULT_CATEGORY"])

        logger.info(f"Search type: {search_type}")

        for sys_id, it_system in kitos_applications.items():
            category_name = it_system['Storm navn'].replace(
                "(STORM)", "").strip() if it_system['Storm navn'] != None else SETTINGS["archimate.DEFAULT_KLASSIFIKATION"]

            cat_node = self.get_named_application_folder(category_name)
            if cat_node == None:
                # Create new category and put it under the default category
                cat_id = SETTINGS["archimate.CATEGORY_ID_PREFIX"] + \
                    str(it_system['Storm ID'])
                cat_node = self.create_application_folder(
                    category_name, cat_id)
                default_category.appendChild(cat_node)
                logger.info(
                    f"New STORM classification created: {category_name}")

            app_node = None
            app_sys_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
                str(sys_id)

            if search_type == 'name':
                logger.info(
                    f"Search for system name: {it_system['Systemnavn']}")
                app_node = self.get_application_element_from_name(
                    it_system['Systemnavn'])
            elif search_type == 'id':
                logger.info(f"Search for system id: {app_sys_id}")
                app_node = self.get_application_element_from_id(
                    app_sys_id)

            if app_node == None:
                app_node = self.create_application_element(
                    it_system['Systemnavn'], app_sys_id)
                cat_node.appendChild(app_node)
                logger.info(
                    f"Application {it_system['Systemnavn']} with id {app_sys_id} created.")

            if app_node.parentNode.getAttribute('name') != category_name:
                # this app entry is old and Storm class for has changed
                # move it to new category
                app_node = self.move_application(
                    app_node, cat_node)

            if app_node.getAttribute('id') != app_sys_id:
                logger.info(
                    f"Updating systemid for {it_system['Systemnavn']}. Old id: {app_node.getAttribute('id')}, new id: {app_sys_id}")
                self.update_application_id(app_node, app_sys_id)

    """
    Update KITOS relations in archimate model. 
    Input is list of relations from KITOS fetched with 
    KitosHelper.return_itsystem_relations()
    """

    def update_application_relations(self, relations):
        # TODO: for relations associted with a KITOS relations, create properties containing
        # frequency
        for index in range(len(relations)):
            relation = relations[index]
            # re-use kitos relation uuid when inserting
            relation_id = relation["uuid"]
            relation_name = ""

            # system source id
            source_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
                str(relation["fromUsage"]["id"])
            target_id = SETTINGS["archimate.APPLICATION_ID_PREFIX"] + \
                str(relation["toUsage"]["id"])

            # First check relations from KITOS and identify known relations in archimate model
            rel_node = self._find_childnode_from_attributes(
                self.relations_folder, "element", {"id": relation_id})

            if rel_node is not None:
                # update source and target if the differ in archimate model from registration in KITOS
                if source_id != rel_node.getAttribute("source") or target_id != rel_node.getAttribute("target"):
                    logger.info(
                        f"Updating relation {relation_id}, setting source to: {source_id} and target to: {target_id}.")
                    rel_node.setAttribute("source", source_id)
                    rel_node.setAttribute("target", target_id)
            else:
                # Now lookup relations in archimate model and set their relationship id to
                # kitos id, if source and target matches
                rel_node = self._find_childnode_from_attributes(
                    self.relations_folder, "element", {"source": source_id, "target": target_id})

                if rel_node is not None:
                    # we found a relation in archimate model with source and target matching an
                    # identical entry in KITOS. Now update the id
                    rel_node.setAttribute("id", relation_id)
                else:
                    # create new relation and use KITOS uuid for relation as identifier
                    logger.info(
                        f"Creating new relation. ID: {relation_id} SOURCE: {source_id} TARGET: {target_id}")
                    lenght_before = len(self.relations_folder.childNodes)
                    new_relation = self.create_relation_element(
                        relation_id, source_id, target_id, relation["description"])
                    self.relations_folder.appendChild(new_relation)
                    lenght_after = len(self.relations_folder.childNodes)
                    logger.info(
                        f"Before: {lenght_before} After: {lenght_after}")

    def get_named_application_folder(self, folder_name):
        return self._find_childnode_from_attributes(self.application_folder, "folder", {"name": folder_name})

    def get_application_element_from_name(self, application_name):
        return self._find_childnode_from_attributes(self.application_folder, "element", {"name": application_name, "xsi:type": "archimate:ApplicationComponent"})

    def get_application_element_from_id(self, application_id):
        return self._find_childnode_from_attributes(self.application_folder, "element", {"id": application_id, "xsi:type": "archimate:ApplicationComponent"})

    def move_application(self, app_node, new_parent_node):

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
