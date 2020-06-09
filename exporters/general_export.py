import json
import os
import pathlib
import string

import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

SETTINGS = json.loads(cfg_file.read_text())


"""
Standard exports from KITOS. 
Exports to excel files that can be saved on disk or streamed to webservice call

The are generic reports that can be used as templates for specific reports for 
each municipality
"""


def export_from_kitos():
    k = KitosHelper(SETTINGS['KITOS_USER'], SETTINGS['KITOS_PASSWORD'],
                    SETTINGS['KITOS_URL'], False, False)
    it_systems = k.return_itsystems()

    export_it_systems(k, it_systems, 'it_systemer.csv')


def export_it_systems(kh, it_systems, filename):

    field_names = {'Systemnavn',
                   'Persondata',
                   'note',
                   'Ansvarlig org. enhed',
                   'Leverandør',
                   'Leverandør ID',
                   'Beskrivelse',
                   'url',
                   'kle',
                   'Storm ID',
                   'Storm navn',
                   'Roller',
                   'Kontrakter'}

    rows = []
    for sys_id, it_system in it_systems.items():
        rows.append(it_system)

    kh._write_csv(field_names, rows, filename)


if __name__ == '__main__':
    kl.start_logging("kitos_export.log")
    export_from_kitos()
