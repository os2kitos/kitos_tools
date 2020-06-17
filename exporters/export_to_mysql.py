import logging
import os
import pathlib
import string
import json

import click
import mysql.connector

import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

SETTINGS = json.loads(cfg_file.read_text())

logger = logging.getLogger("mysql-export")


def export_to_mysql():
    """
    Exports datafrom KITOS  from to a local mysqlx compatible instance.
    The data stored in the mysql database can be used with the web application "Softwareoversigten"

    :param server: The Kitos server to connect ot
    :type server: string
    :param username: Kitos user with API access
    :type username: string
    :param password: Password for Kitos user with API access
    :type password: string
    """

    logger.info("Export to mysql started")

    kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                     SETTINGS['KITOS_URL'], False, False)
    it_systems = kh.return_itsystems()

    rows = []
    for sys_id, it_system in it_systems.items():

        # Read roles and responsible, operational res., contact person and test responsible
        rights = it_system['Roller']
        user_info = {"name": "", "email": ""}
        roles = {"Systemejer": user_info,
                 "Kontaktperson": user_info,
                 "Systemansvarlig": user_info,
                 "Testansvarlig": user_info,
                 "OnPremise koordinator": user_info}

        roles.update(rights)

        # Find suppliername, dpo suppliername and cvr
        # iterate through contracts and extract information

        main_contract_id = it_system['Hovedkontrakt ID']
        contracts = it_system['Kontrakter']

        has_dba = "Nej"
        dba_info = {"supplier_name": "",
                    "supplier_cvr": "",
                    "dba_link": "Nej",
                    "dba_note": "",
                    "contract_id": 0}

        # dba_link is either to contract in KITOS or the entry found in it_system['dba_url'] depending on how
        # the data has been entered
        # supplier name and cvr only available if dba is registered through contract
        # If a contract is of type "Databehandler aftale" it is shown in GDPR
        # If a contract is of another type but under it system relation is marked as covering "Databehandleraftale"
        # it is also valid for this system.

        # Does main contract contain DBA elements, if so use this.

        for contract_id, contract in contracts.items():
            if contract['Type'] == "Databehandleraftale" or "Databehandleraftale" in contract['Aftaleelementer']:
                dba_info['supplier_name'] = contract['Leverandør']
                link = "<a href=\"https://kitos.dk/#/contract/edit/" + \
                    str(contract['Kontrakt ID']) + \
                    "/main\">Databehandleraftale</a>"
                dba_info['dba_link'] = link
                dba_info['contract_id'] = contract['Kontrakt ID']
                has_dba = "Ja"
                break

        if has_dba == "Nej" and it_system['dba_url'] is not None and it_system['dba_name'] is not None:
            # No contract with DBA elements found, but link been entered manually
            # this is incorrect registration!
            link = "<a href=\"" + \
                it_system['dba_url'] + "\">" + it_system['dba_name'] + "</a>"
            dba_info['dba_link'] = link
            dba_info['dba_note'] = str(it_system['dba_note'])

            # is critical?
        is_critical = "Nej" if it_system['isBusinessCritical'] == 0 else "Ja"

        row = (sys_id,
               it_system['uuid'],
               it_system['Leverandør'],
               it_system['Systemnavn'],
               it_system['Kaldenavn'],
               it_system['Beskrivelse'],
               it_system['url'],
               json.dumps(it_system['kle'], ensure_ascii=False),
               it_system['note'],
               it_system['BusinessTypeName'],
               roles['Systemejer']['name'],
               roles['Systemejer']['email'],
               roles['Systemansvarlig']['name'],
               roles['Systemansvarlig']['email'],
               roles['Kontaktperson']['name'],
               roles['Kontaktperson']['email'],
               it_system['Ansvarlig org. enhed'],
               roles['Testansvarlig']['name'],
               roles['Testansvarlig']['email'],
               it_system['Persondata'],
               dba_info['dba_link'],
               is_critical,
               dba_info['dba_note'],
               "N/A",
               dba_info['supplier_cvr'],
               dba_info['supplier_name']
               )
        rows.append(row)

    update_itsystems(rows)


def update_itsystems(rows):
    try:
        conn = mysql.connector.connect(
            host=SETTINGS['mysql.HOST'], database=SETTINGS['mysql.DB'], user=SETTINGS['mysql.USER'], password=SETTINGS['mysql.PASSWORD'])

        if not conn.is_connected():
            raise mysql.connector.Error(msg=f"Could not connect to database")

        data_table = SETTINGS['mysql.SYSTEMS_TABLE']

        cursor = conn.cursor()
        # Reset data table
        cursor.execute(f"Truncate table {data_table}")

        query = "INSERT INTO cached_data(kitosID, \
                                        UUID, \
                                        SupplierName, \
                                        Name, \
                                        LocalName, \
                                        Description, \
                                        Url, \
                                        KleName, \
                                        Note, \
                                        BusinessType, \
                                        SystemOwner_name, \
                                        SystemOwner_email, \
                                        OperationalResponsible_name, \
                                        OperationalResponsible_email, \
                                        ContactPerson_name, \
                                        ContactPerson_email, \
                                        ResponsibleOrganizationalUnit, \
                                        TestResponsible_name, \
                                        TestResponsible_email, \
                                        DataLevel, \
                                        DataHandlerAgreement, \
                                        BusinessCritical, \
                                        NoteUsage, \
                                        UsedBy, \
                                        DataHandlerSupplierCvr, \
                                        DataHandlerSupplierName) \
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        cursor.executemany(query, rows)

        conn.commit()

    except mysql.connector.Error as e:
        logger.error(f"Got error when connecting to mysql db: {e}")

    finally:

        cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    kl.start_logging("mysql_export.log")
    export_to_mysql()
