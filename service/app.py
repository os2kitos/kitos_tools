# coding=utf-8
import os
import string
import secrets

from flask import Flask, session, jsonify
# from flask.ext.session import Session


from kitos_helper.kitos_helper import KitosHelper

app = Flask(__name__)
#app = Flask(__name__.split('.')[0])

# forbereder random app secret for session storage
alphabet = string.ascii_letters + string.digits
secret_key = ''.join(secrets.choice(alphabet) for i in range(8))

# secret key til session håndtering
app.secret_key = secret_key

# Sørger for at Kitos brugernavn og password bliver sat - dette kunne med fordel blive sat i f.eks. docker
# I Pycharm kan det sættes via runtime environment i settings
KITOS_USER = os.environ['KITOS_USER']
KITOS_PASSWORD = os.environ['KITOS_PASSWORD']
KITOS_URL = os.environ['KITOS_URL']
FLASK_APP_DEBUG: int = int(os.environ['FLASK_DEBUG'])


@app.route('/')
def index_page():
    # todo: simpel oversigt over funktionalitet og simple instrukser om hvordan man konfigurerer dette i et
    #  automatiseret setup
    kh = KitosHelper(KITOS_USER, KITOS_PASSWORD, KITOS_URL, False, False)
    return f'Total number of systems in use:{kh.return_itsystems_count()}'


@app.route('/connect_status')
def connect_status():
    # todo: Denne metode er beregnet til at lave et hurtigt tjek af om brugers login er gyldigt, og om Kitos API'et
    #  kører
    return 'to be implemented'


@app.route('/kitoskommuneid')
def show_kitos_kommuneid():
    # todo: Denne metode er beregnet til at lave et hurtigt tjek af om brugers login er gyldigt, og om Kitos API'et
    #  kører
    kh = KitosHelper(KITOS_USER, KITOS_PASSWORD, KITOS_URL, False, False)
    return f'Aktuelle kommuneid: {kh.return_kitos_kommuneid()}'

@app.route('/itsystemer')
def list_systemer():
    # todo: denne metode er beregnnet til at hente en liste over IT systemer - det skal nærmere vurderes detajlegrad
    return 'to be implemented'


# Verdens bedste ændringer fra Anders
@app.route('/get_token', methods=['POST', 'GET'])
def display_token():
    """
    Denne metode skal på sigt fjernes da den reelt kun tjener det formål at vise at det token man beder om bliver
    stillet til rådighed
    :return: string
    """

    kh = KitosHelper(KITOS_USER, KITOS_PASSWORD, KITOS_URL, False, False)
    return kh.token


@app.route('/itsystems_in_use')
def systemer_i_brug():
    kh = KitosHelper(KITOS_USER, KITOS_PASSWORD, KITOS_URL, False, False)
    it_systems = kh.return_itsystems()
    return jsonify(it_systems)


if __name__ == '__main__':
    if FLASK_APP_DEBUG == 1:
        app.run(host='0.0.0.0', debug=True, port='5010')
    else:
        app.run(host='0.0.0.0', debug=False, port='5010')
