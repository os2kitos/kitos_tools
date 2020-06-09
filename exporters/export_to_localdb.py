import os
import string
import click
import logging


from kitos_helper.kitos_helper import KitosHelper
import kitos_helper.kitos_logger as kl

"""
Exports datafrom KITOS  from to a local mysqlx compatible instance. 

The data stored in the mysql database can be used with the web application "Softwareoversigten"
"""

logger = logging.getLogger("mysql-export")


@click.command()
@click.option('--prod', 'server', flag_value='https://kitos.dk', help='https://kitos.dk')
@click.option('--test', 'server', flag_value='https://kitostest.miracle.dk', help='https://kitostest.miracle.dk')
@click.option('--username', help='UserID for user with API access')
@click.option('--password', help='Password for user')
def export_to_mysql(server, username, password):

    logger.info("Export to mysql started")

    kh = KitosHelper(username, password, server, False, True)
    it_systems = kh.return_itsystems()

    for it_id, it_system in it_systems.items():
        it_org_usage = kh.return_isystem_usage(it_id)


if __name__ == '__main__':
    kl.start_logging("mysql_export.log")
    export_to_mysql()
