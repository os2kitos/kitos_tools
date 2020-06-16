#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import pathlib
import string
import click
import logging
import pandas as pd
from pandas import json_normalize
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import null
from sqlalchemy import types

from kitos_helper.kitos_helper import KitosHelper
import kitos_helper.kitos_logger as kl

"""
Exports datafrom KITOS  from to a local mysqlx compatible instance. 

The data stored in the mysql database can be used with the web application "Softwareoversigten"
"""

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

logger = logging.getLogger("mysql-export")

SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))

@click.command()
@click.option('--prod', 'server', flag_value='https://kitos.dk', help='https://kitos.dk')
@click.option('--test', 'server', flag_value='https://kitostest.miracle.dk', help='https://kitostest.miracle.dk')
@click.option('--username', help='UserID for user with API access')
@click.option('--password', help='Password for user')
def export_to_mysql(server, username, password):

    logger.info("Export to mysql started")

    if not password:
        kh = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                         SETTINGS['KITOS_URL'], False, False)
    else:
        kh = KitosHelper(username, password, server, False, True)

    it_systems = kh.return_itsystems_softwareoversigt()
    #it_systems = kh.return_itsystems()

    # organiser efter indhold af dict istedet for den numeret liste struktur. 
    dataframe = pd.DataFrame.from_records(it_systems)
    dataframe = pd.DataFrame.from_dict(it_systems, orient='index')

    #it_org_usage_list = []
    dataframe.info()

    #dataframe.to_excel("test_regneark.xlsx")
    #dataframe.to_csv("test_regneark_text.csv")

    connectString = ("mysql+pymysql://"+SETTINGS['DB_USR']+":"+
                    SETTINGS['DB_PWD']+"@"+SETTINGS['DB_HOST']+
                    "/"+SETTINGS['DB_DB']+"?charset=utf8mb4")
    engine = create_engine(connectString, echo=False)
    
    with engine.connect() as conn, conn.begin():
        dataframe.to_sql('jsontest1', conn, if_exists='replace', index=True, chunksize=1, dtype={'kle': types.JSON, 'Roller': types.JSON, 'Kontrakter': types.JSON})

if __name__ == '__main__':
    kl.start_logging("mysql_export.log")
    export_to_mysql()
