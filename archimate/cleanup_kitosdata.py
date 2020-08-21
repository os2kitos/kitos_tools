import os
import json
import pathlib
import click
import logging


import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

import archimate_helper as ah

cfg_file = pathlib.Path.cwd() / 'settings' / 'settings.json'
if not cfg_file.is_file():
    raise Exception('No setting file')

logger = logging.getLogger("kitos-archimate")


SETTINGS = json.loads(cfg_file.read_text(encoding='utf-8'))


# TODO:
# - Flyt alle systemer i archimate som ikke findes i KITOS ind under "Andre"->"Ikke klassificerede"
# - Systemer som er i archimate og som har været i kitos flyttes til "Andre"->"Ikke i KITOS"
# - Ryd op i roller/aktører der importeret
# - Lav funktion til at skifte et uuid ud med et andet i alle relationer. Bruges når der et
# manuelt oprettet it system som erstattes med et korrekt system fra kitos. "ReplaceFromKitos"
