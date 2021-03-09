# coding=utf-8
import codecs
import csv
import json
import logging
import os
from typing import Type

import requests

logger = logging.getLogger("kitos-helper")


class KitosHelper:
    token: Type[str]
    user_orgID: Type[int]

    def __init__(self, username, password, host='https://kitos.dk', export_ansi=True,
                 use_cache=True):

        self.token = None
        self.cache = {}
        self.use_cache = use_cache
        self.export_ansi = export_ansi
        self.KITOS_URL = host
        self.KITOS_USER = username
        self.KITOS_PASSWORD = password
        self.KITOS_KOMMUNEID = ''
        self._connect()  # henter API token

    def _kitos_get(self, url, params={}):
        # TODO: add some try/catch handling of http request errors
        full_url = f"{self.KITOS_URL}/{url}"

        if (full_url in self.cache) and self.use_cache:
            return_dict = self.cache[full_url]
        else:
            if self.token is None:
                # Throw some exception
                return_dict = None
            else:
                header = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(
                    full_url,
                    headers=header,
                    params=params
                )
                if response.status_code == 401:
                    msg = 'Invalid token'
                    logger.error(msg)
                    raise requests.exceptions.RequestException(msg)
                return_dict = response.json()

            self.cache[full_url] = return_dict

        return return_dict

    def _kitos_post(self, url, payload):

        if self.token is None:
            header = None
        else:
            header = {"Authorization": f"Bearer {self.token}"}

        full_url = f"{self.KITOS_URL}/{url}"
        response = requests.post(
            full_url,
            headers=header,
            json=payload
        )
        return response

    def _connect(self):
        response = self._kitos_post('api/authorize/gettoken',
                                    {
                                        "email": f"{self.KITOS_USER}",
                                        "password": f"{self.KITOS_PASSWORD}"
                                    })
        if response.status_code == 401:
            msg = 'Invalid token'
            logger.error(msg)
            raise requests.exceptions.RequestException(msg)
        else:

            logger.info('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            logger.info('Response HTTP Response Body: {content}'.format(
                content=response.content))

            json_data = response.json()
            self.token = json_data['response']['token']

            json_data = self._kitos_get("api/authorize/GetOrganizations")
            self.KITOS_KOMMUNEID = json_data['response'][0]['id']

    def _write_csv(self, fieldnames, rows, filename):
        """
        Write a csv-file from a a dataset. Only fields explicitly mentioned
        in fieldnames will be saved, the rest will be ignored.

        :param fieldnames: The headline for the columns, also act as filter.
        :type fieldnames: [type]
        :param rows: A list of dicts, each list element will become a row, keys
        in dict will be matched to fieldnames.
        :type rows: [type]
        :param filename: The name of the exported file.
        :type filename: [type]
        """

        print('Encode ascii: {}'.format(self.export_ansi))
        with open(filename, encoding='utf-8', mode='w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                    extrasaction='ignore',
                                    delimiter=';',
                                    quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        if self.export_ansi:
            with codecs.open(filename, 'r', encoding='utf-8') as csvfile:
                lines = csvfile.read()
            with codecs.open(filename, 'w',
                             encoding='cp1252') as csvfile:
                csvfile.write(lines)

    def _get_odata_itsystems_usage(self):
        """
        Denne metode henter en liste over de systemer der anvendes af kommunen - den henter kun de data ud der skal bruges til at lave Archimate XML'en
        :return:
        """
        try:
            response = requests.get(
                url=f"{self.KITOS_URL}/odata/Organizations({self.KITOS_KOMMUNEID})/ItSystemUsages",
                params={
                    "$expand": "ItSystem($select=Name,Description,Uuid,Url,DataLevel,ContainsLegalInfo;"
                               "$expand="
                               # "AppTypeOption($select=Name,Description),	"
                               # "BusinessType($select=Name,Description),	"
                               "Parent($select=Name,Description,Uuid,Url;$expand=BusinessType($select=Name,Description)),"
                               "TaskRefs($select=TaskKey)"
                               ","
                               ")",
                    "$format": "json",
                    "$top": "5000",
                    "$orderby": "ItSystem/Name",
                    "$count": "true",
                    "$select": "Id, UserCount",
                },
                headers={
                    "Authorization": f"Bearer {self.token}",
                },
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))

            json_data = response.json()
            return json_data
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

    def _get_itsystems_count(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        json_data = self._get_itsystems_usage()
        return len(json_data)

    def _get_itsystems_usage(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        it_systems = []

        is_last_page = False
        query_url = "api/ItSystemUsage"
        page_number = 0

        while not is_last_page:
            skip = page_number * 100
            response = self._kitos_get(query_url,
                                       {
                                           "organizationId": self.KITOS_KOMMUNEID,
                                           "take": "100",
                                           "skip": str(skip)
                                       })
            if len(response['response']) > 0:
                it_systems.extend(response['response'])
                page_number += 1
            else:
                is_last_page = True

        return it_systems

    def return_itsystems_count(self):
        return self._get_itsystems_count()

    def _read_kle_from_itsystem(self, it_system):
        kle_data = []

        for kle in it_system['taskRefs']:
            kle_data.append(
                {"TaskKey": kle['taskKey'], "Description": kle['description']})

        return kle_data

    def _read_rights_from_itsystem(self, it_system_rights):
        rights = {}

        for right in it_system_rights:
            user_name = right['user']['name'] + \
                " " + right['user']['lastName']

            rights.update(
                {right['roleName']: {"name": user_name, "email": right['userEmail']}})

        return rights

    def _read_contracts_from_itsystem(self, it_system_contracts):
        contracts = {}

        for c_data in it_system_contracts:
            c_elements = []
            for ce in c_data['agreementElements']:
                c_elements.append(ce['name'])

            contract = {
                'Navn': c_data['name'],
                'Kontrakt ID': c_data['id'],
                'Leverandør': c_data['supplierName'],
                'Type': c_data['contractTypeName'],
                'Aftaleelementer': c_elements,
            }
            contracts.update({c_data['id']: contract})

        return contracts

    def convert_sensitity_level(self, level_data):
        level = ""
        levels = ["Ingen persondata", "Almindelige persondata",
                  "Følsomme persondata", "Straffedomme og lovovertrædelser"]

        for slevel in level_data:
            level = levels[slevel['dataSensitivityLevel']]

        return level

    def return_itsystems(self):
        # hent liste over anvendte IT systemer ud fra kommuneID i Kitos
        # it_systems = self._get_odata_itsystems_usage()

        # Rewrite scructure for IT Systems
        json_data = self._get_itsystems_usage()

        #json_itsystems = json.dumps(json_data)
        #f = open("itsystems.json", "w")
        # f.write(json_itsystems)
        # f.close()

        it_systems = {}

        for it_system in json_data:
            description = it_system['itSystem']['description']
            if description is not None:
                description = description.replace("\n", " ").replace("\r", " ")

            system_url = "https://kitos.dk/#/system/usage/" + \
                str(it_system['id']) + "/main"

            # dba_url = "https://kitos.dk/#/data-processing/edit/" + str(it_system[]) + "/main"

            it_systems.update({it_system['id']: {
                'Systemnavn': it_system['itSystem']['name'],
                'Kaldenavn': it_system['localCallName'],
                'uuid': it_system['itSystem']['uuid'],
                'Persondata': self.convert_sensitity_level(it_system['sensitiveDataLevels']),
                'note': it_system['note'],
                'Ansvarlig org. enhed': it_system['responsibleOrgUnitName'],
                'Leverandør': it_system['itSystem']['belongsToName'],
                'Leverandør ID': it_system['itSystem']['belongsToId'],
                # replace newlines in descripts
                'Beskrivelse': description,
                'url': system_url,
                'kle': self._read_kle_from_itsystem(it_system['itSystem']),
                'Storm ID': it_system['itSystem']['businessTypeId'],
                'Storm navn': it_system['itSystem']['businessTypeName'],
                'Roller': self._read_rights_from_itsystem(it_system['rights']),
                'Hovedkontrakt ID': it_system['mainContractId'],
                'Kontrakter': self._read_contracts_from_itsystem(it_system['contracts']),
                'BusinessTypeName': it_system['itSystem']['businessTypeName'],
                'isBusinessCritical': it_system['isBusinessCritical'],
                # 'dba_name': it_system['linkToDirectoryUrlName'],
                # 'dba_url': it_system['linkToDirectoryUrl'],
                # 'dba_note': it_system['noteUsage'],
                # 'dba_workers': it_system['associatedDataWorkers'],
                'dba_name': "",
                'dba_url': "",
                'dba_note': "",
                'dba_workers': ""
            }})

        return it_systems

    def return_isystem_usage(self, system_id):
        """[summary]

        :param system_id: [description]
        :type system_id: [type]
        :return: [description]
        :rtype: [type]
        """
        json_data = self._kitos_get(
            f"api/ItSystemUsageOrgUnitUsage/{system_id}")
        return json_data['response']

    def return_itsystem_relations(self):
        system_relations = []

        is_last_page = False
        query_url = f"api/v1/systemrelations/defined-in/organization/{self.KITOS_KOMMUNEID}"
        page_number = 0
        while not is_last_page:
            response = self._kitos_get(query_url,
                                       {
                                           "pageNumber": str(page_number),
                                           "pageSize": "100",
                                       })
            if len(response['response']) > 0:
                system_relations.extend(response['response'])
                page_number += 1
            else:
                is_last_page = True

        return system_relations
