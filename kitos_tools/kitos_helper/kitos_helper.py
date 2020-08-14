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
            #self.KITOS_KOMMUNEID = json_data['response']['activeOrganizationId']

            return json_data

    def _write_csv(self, fieldnames, rows, filename):
        """ Write a csv-file from a a dataset. Only fields explicitly mentioned
        in fieldnames will be saved, the rest will be ignored.
        :param fieldnames: The headline for the columns, also act as filter.
        :param rows: A list of dicts, each list element will become a row, keys
        in dict will be matched to fieldnames.
        :param filename: The name of the exported file.
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
        json_data = self._get_itsystems_usage()
        return len(json_data['response'])

    def _get_kitos_kommuneid(self):
        return self.KITOS_KOMMUNEID

    def _get_itsystems_usage(self):
        return self._kitos_get("api/ItSystemUsage",
                               {
                                   #"organizationId": self.KITOS_KOMMUNEID,
                                   #"q": "",
                               })

    def _set_kitos_kommuneid(self):
        json_data = self._get_organizationId()
        self.KITOS_KOMMUNEID = json_data['response']['id']
        #return 
                            
    def _get_organizationId(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self._kitos_get("api/authorize/GetOrganizations",{})
                               #"organizationId": self.KITOS_KOMMUNEID,
                               #GetOrganizations

    def return_kitos_kommuneid(self):
        return self.KITOS_KOMMUNEID

    def return_itsystems_count(self):
        return self._get_itsystems_count()

    def _read_kle_from_itsystem(self, it_system):
        kle_data = {}

        for kle in it_system['taskRefs']:
            kle_data.update({kle['taskKey']: kle['description']})

        return kle_data

    def _read_rights_from_itsystem(self, it_system_rights):
        rights = {}

        for right in it_system_rights:
            rights.update({right['roleName']: right['userEmail']})

        return rights

    def _read_url_from_itsystem(self, it_system_externalReferences):
        urls = {}

        #print(it_system_externalReferences)

        for url in it_system_externalReferences:
            
            urls.update({url['title']: url['url']})

        return urls
    
    def _read_dataWorker_from_itsystem(self, it_system_associatedDataWorkers):
        dataWorkers = {}

        for dataWorker in it_system_associatedDataWorkers:
            dataWorkers.update({dataWorker['dataWorkerName']: dataWorker['dataWorkerCvr']})

        return dataWorkers

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

    def return_itsystems(self):
        # hent liste over anvendte IT systemer ud fra kommuneID i Kitos
        # it_systems = self._get_odata_itsystems_usage()

        # Rewrite scructure for IT Systems
        json_data = self._get_itsystems_usage()

        it_systems = {}

        for it_system in json_data['response']:
            it_systems.update({it_system['id']: {
                'Systemnavn': it_system['itSystem']['name'],
                'Persondata': it_system['sensitiveDataTypeName'],
                'note': it_system['note'],
                'Ansvarlig org. enhed': it_system['responsibleOrgUnitName'],
                'Leverandør': it_system['itSystem']['belongsToName'],
                'Leverandør ID': it_system['itSystem']['belongsToId'],
                'Beskrivelse': it_system['itSystem']['description'],
                'url': '',  # it_system['itSystem']['url'],
                'kle': self._read_kle_from_itsystem(it_system['itSystem']),
                'Storm ID': it_system['itSystem']['businessTypeId'],
                'Storm navn': it_system['itSystem']['businessTypeName'],
                'Roller': self._read_rights_from_itsystem(it_system['rights']),
                'Hovedkontrakt ID': it_system['mainContractId'],
                'Kontrakter': self._read_contracts_from_itsystem(it_system['contracts']),
            }})

        return it_systems

    def return_itsystems_softwareoversigt(self):

        json_data = self._get_itsystems_usage()

        with open('itsystem.json', 'w') as outfile:
            json.dump(json_data, outfile)

        it_systems = {}

        for it_system in json_data['response']:

            system_url = "https://kitos.dk/#/system/usage/" + \
                str(it_system['id']) + "/main"

            it_systems.update({it_system['id']: {
                'Systemnavn': it_system['itSystem']['name'],
                'Persondata': it_system['sensitiveDataTypeName'],
                'note': it_system['note'],
                'Ansvarlig org. enhed': it_system['responsibleOrgUnitName'],
                'Leverandør': it_system['itSystem']['belongsToName'],
                'Leverandør ID': it_system['itSystem']['belongsToId'],
                'Beskrivelse': it_system['itSystem']['description'],
                'url': system_url,
                'kle': self._read_kle_from_itsystem(it_system['itSystem']),
                'Storm ID': it_system['itSystem']['businessTypeId'],
                'Storm navn': it_system['itSystem']['businessTypeName'],
                'Roller': self._read_rights_from_itsystem(it_system['rights']),
                'Hovedkontrakt ID': it_system['mainContractId'],
                'Kontrakter': self._read_contracts_from_itsystem(it_system['contracts']),
                'Forretningstype': it_system['itSystem']['businessTypeName'],
                'Forretningskritisk': it_system['isBusinessCritical'],
                'dba_name': it_system['linkToDirectoryUrlName'],
                'dba_url': it_system['linkToDirectoryUrl'],
                'dba_note': it_system['noteUsage'],
                'dba_workers': it_system['associatedDataWorkers'],
                'uuid': it_system['itSystem']['uuid'],
                'LocalName': it_system['localCallName'],
                # Er under roller!
                #'TestResponsible_name': it_system['rights']['userName'],
                #'OperationalResponsible_email': it_system['risks']['responsibleUser']['email'],
            }})

        return it_systems

    def return_isystem_usage(self, system_id):
        json_data = self._kitos_get(
            f"api/ItSystemUsageOrgUnitUsage/{system_id}")
        return json_data['response']

    def return_raw_json_response(self):
        return self._get_itsystems_usage()
