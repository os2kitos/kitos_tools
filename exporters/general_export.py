import os
import string
import click

from kitos_helper.kitos_helper import KitosHelper
import kitos_helper.kitos_logger as kl

"""
Standard exports from KITOS. 
Exports to excel files that can be saved on disk or streamed to webservice call

The are generic reports that can be used as templates for specific reports for 
each municipality
"""


@click.command()
@click.option('--prod', 'server', flag_value='https://kitos.dk', help='https://kitos.dk')
@click.option('--test', 'server', flag_value='https://kitostest.miracle.dk', help='https://kitostest.miracle.dk')
@click.option('--username', help='UserID for user with API access')
@click.option('--password', help='Password for user')
def export_from_kitos(server, username, password):
    k = KitosHelper(username, password, server, False, False)
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
