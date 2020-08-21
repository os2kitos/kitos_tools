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
# Tilføj os2mo-eksport-import-data/os2mo-helper som afhængig via pip
# Forespørg MO og hent organisation ind i archimate model
# Org. enheder = business actors
#
# # Chef titler = business roles med relation til enhed leder aktør
# medarbejder funktionsbeskriveler = business roles med relationer til medarbejder aktør i en enhed
# Aktørnavn  er <enhed navn> Leder og <enhed navn> medarbejder
# business roles navne er funktionsbeskrivelser
# Org enheders KLE, fuld sti = Business services, serving relationship fra enheds aktør
