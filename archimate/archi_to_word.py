import os
import json
import pathlib
import click
import logging


import kitos_helper.kitos_logger as kl
from kitos_helper.kitos_helper import KitosHelper

import archimate_helper as ah


def export_to_word():
    print("Exports diagram from Archimatemodel to word")


if __name__ == '__main__':
    kl.start_logging("archimate_to_word.log")
    export_to_word()
