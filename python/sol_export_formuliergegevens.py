#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import yaml


credentials = yaml.safe_load(open("credentials.yaml"))['credentials']
hit_config = yaml.safe_load(open("hit.yaml"))

hit = [hit for hit in hit_config['hits'] if hit['year'] == hit_config['current_year']][0]
OUTPUT_DIR = f"hit-{hit_config['current_year']}"


# Colors
class c:
    YELLOW = '\033[1;33m'
    GREEN = '\033[1;32m'
    NC = '\033[0m' # No Color

s = requests.Session()


def printStep(number, description):
    print(f"{c.YELLOW}Step {number}:{c.NC} {description}...", end=' ', flush=True)

def printOk():
    print(f"[{c.GREEN}OK{c.NC}]\n")


def login(credentials):
    printStep(1, 'Using login button')
    response = s.post("https://sol.scouting.nl/rs/user/", data = {
        'submitBtn': 'Log+in'
    })
    contents = BeautifulSoup(response.content, "html.parser")
    printOk()

    inputs = {n['name']: n['value'] for n in contents.find_all('input')}

    printStep(2, f"Logging on {credentials['username']} at login.scouting.nl")
    s.post("https://login.scouting.nl/provider/authenticate", data = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.return_to': 'https://sol.scouting.nl/rs/user/?perform=loginDone',
        'openid.realm': 'https://sol.scouting.nl/',
        'openid.ns_theme': 'https://login.scouting.nl/ns/theme/1.0',
        'openid.theme_theme': 'TC3_leaf',
        'openid.assoc_handle': inputs['openid.assoc_handle'],
        'token': inputs['token'],
        'username': credentials['username'],
        'password': credentials['password'],
        'form_action': 'Inloggen'
    })
    printOk()


def accept_export_terms():
    printStep(3, 'Accepting export terms')
    s.post("https://sol.scouting.nl/support/filter/export", data = {
        'redirectURI': 'https://sol.scouting.nl',
        'support_ok_with_export_terms': '',
        'support_ok_with_export_terms[1]': '1',
        'submitBtn': 'Download'
    })
    printOk()


def download(form_id, hit):
    printStep(4, f"Finding linked forms for {form_id}")

    response = s.get(f"https://sol.scouting.nl/as/form/{form_id}/report")
    contents = BeautifulSoup(response.content, "html.parser")
    linked_forms_ids = [option['value'] for option in contents.find('select', attrs = {'name': 'linked_forms[]'}).find_all('option') ]

    printOk()

    printStep(5, 'Downloading formuliergegevens')

    data = {
        'button': 'part_data_linked',
        'prt_st_id[]': hit['participant_status'],
        'linked_forms[]': linked_forms_ids,
        'submitBtn': 'submitBtn'
    }

    response = s.post(f"https://sol.scouting.nl/as/form/{form_id}/report", data)

    fo = open(f"{OUTPUT_DIR}/formuliergegevens_{form_id}.csv", "w")
    fo.write(response.text)
    fo.close()
    printOk()

    printStep(6, 'Downloading subgroepen')
    data = {
        'button': 'team_data_linked',
        'prt_st_id[]': hit['participant_status'],
        'linked_forms[]': linked_forms_ids,
        'submitBtn': 'submitBtn'
    }

    response = s.post(f"https://sol.scouting.nl/as/form/{form_id}/report", data)
    fo = open(f"{OUTPUT_DIR}/subgroepen_{form_id}.csv", "w")
    fo.write(response.text)
    fo.close()
    printOk()


def clean_up():
    printStep(7, 'Cleaning up')
    # ???
    printOk()


#
# Main Program
#
login(credentials)
accept_export_terms()

for form_id in hit['forms']:
    download(form_id, hit)

clean_up()
