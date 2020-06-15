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
    it_systems = kh.return_itsystems()

    # organiser efter indhold af dict istedet for den numeret liste struktur. 
    dataframe = pd.DataFrame.from_records(it_systems)
    dataframe = pd.DataFrame.from_dict(it_systems, orient='index')

    #it_org_usage_list = []
    dataframe.info()

##    json_response = kh.return_raw_json_response()['response']
    #json_read = read(json_response)
##    data = json.loads(json.dumps(json_response))
##    json_data = json_normalize(data)

    #json_data = pd.read_json(kh.return_raw_json_response()['response'],orient='index')

    #dataframeRaw = json_normalize(json_data)

    #dataframeRaw = json_data.set_index('id')
##    dataframeRaw = pd.DataFrame.from_records(json_data)
    #dataframeRaw = pd.DataFrame.from_dict(json_data, orient='index')

    #dataframeRaw = pd.read_json(json_data,orient='index')
    #dataframeRaw = json_data
##    dataframeRaw.info()

##    print(dataframeRaw.head())

    #pd.set_option('display.max_columns', 500)

    # Gemmer 'rå' output til json fil.
    # with open('output.json', 'w') as outfile:
    #   json.dump(it_systems, outfile)

#     <class 'pandas.core.frame.DataFrame'>
# Int64Index: 412 entries, 19966 to 33981
# Data columns (total 14 columns):
#  #   Column                Non-Null Count  Dtype
# ---  ------                --------------  -----
#  0   Systemnavn            412 non-null    object
#  1   Persondata            49 non-null     object
#  2   note                  152 non-null    object
#  3   Ansvarlig org. enhed  400 non-null    object
#  4   Leverandør            412 non-null    object
#  5   Leverandør ID         412 non-null    int64
#  6   Beskrivelse           404 non-null    object
#  7   url                   412 non-null    object
#  8   kle                   412 non-null    object
#  9   Storm ID              402 non-null    float64
#  10  Storm navn            402 non-null    object
#  11  Roller                412 non-null    object
#  12  Hovedkontrakt ID      174 non-null    float64
#  13  Kontrakter            412 non-null    object
# dtypes: float64(2), int64(1), object(11)
# memory usage: 48.3+ KB

    #dataframe.to_excel("test_regneark.xlsx")

    #dataframe2NaN = dataframe.astype(object).where(pd.notnull(dataframe), None)
    #dataframe.to_string()
    # print(dataframe.index)
    # print(dataframe.head())
    # print(dataframe.tail(3))
    # print(dataframe.describe())
    


    engine = create_engine('mysql+pymysql://kitos_ext:kitos@20admiis115/kitos?charset=utf8mb4', echo=True)#, json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
    #engine = create_engine('sqlite:///test_sqlite.db', echo=True)
    with engine.connect() as conn, conn.begin():
        #conn.execute(table.insert(), json_value=null())
        # print(type(conn))
        # inspector = inspect(engine)
        # print(inspector.get_table_names())
        # print(inspector.get_columns('EX1'))
        # dataframe.to_sql('jsontest2', conn, if_exists='append', index=False)
        dataframe.to_sql('jsontest3', conn, if_exists='replace', index=True, chunksize=1)

# sqlite3.InterfaceError: Error binding parameter 8 - probably unsupported type.

if __name__ == '__main__':
    kl.start_logging("mysql_export.log")
    export_to_mysql()
