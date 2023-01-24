import os
import requests
from bs4 import BeautifulSoup

import sol_mfa

from sol_export.AnsiColors import AnsiColors as c
from sol_export.Stepper import Stepper


class SolStepper(Stepper):

    def __init__(self, hit_config):
        super().__init__()
        self.hit_config = hit_config
        self.output_dir = self.ensure_output_dir()
        self.hit = self.determine_hit_year()
        self.session = requests.Session()


    def determine_hit_year(self):
        # bepaal instellingen voor dit jaar
        return [hit for hit in self.hit_config['hits'] if hit['year'] == self.hit_config['current_year']][0]


    def ensure_output_dir(self):
        # zorg ervoor dat er een directory komt waar alles neergezet kan worden
        result = f"hit-{self.hit_config['current_year']}"

        if os.path.exists(result):
            if os.path.isfile(result):
                print("OUTPUTDIR bestaat, maar is een bestand!")
        else:
            print("OUTPUTDIR bestaat nog niet, wordt gemaakt.")
            os.mkdir(result)
        return result


    def check_title(self, contents, expected: str) -> bool:
        title = contents.find_all('title')[0]
        return expected in title


    def set_up(self, credentials):
        self.login(credentials)
        self.accept_export_terms()


    def login(self, credentials):

        self.nextStep('Open SOL')
        response = self.session.get('https://sol.scouting.nl')
        contents = BeautifulSoup(response.content, "html.parser")
        token = contents.find_all('input', {'name' : 'token'})[0]['value']
        self.endStep(self.check_title(contents, 'Scouts Online '))
        

        self.nextStep('Using login button')
        response = self.session.post("https://sol.scouting.nl/rs/user/", data = {
            'token': token,
            'submitBtn': 'Log+in'
        })
        contents = BeautifulSoup(response.content, "html.parser")
        inputs = {n['name'] : (n['value'] if n.has_attr('value') else None) for n in contents.find_all('input')}
        self.endStep(self.check_title(contents, 'Inloggen bij Scouting Nederland'))


        self.nextStep(f"Logging on {credentials['sol']['username']} at login.scouting.nl")
        response = self.session.post("https://login.scouting.nl/provider/authenticate", data = {
            'username': credentials['sol']['username'],
            'password': credentials['sol']['password'],
            '_csrf_token': inputs['_csrf_token']
        })
        contents = BeautifulSoup(response.content, "html.parser")
        self.endStep(self.check_title(contents, 'Multifactor authenticatie code invoeren'))


        self.nextStep(f"Retrieving MFA code from gmail")
        last_code = sol_mfa.get_mfa_token_from_mailbox(
            credentials['gmail']['username'],
            credentials['gmail']['password'],
            credentials['gmail']['folder']
        )
        self.endStep(self.check_title(contents, 'Multifactor authenticatie code invoeren'))


        self.nextStep(f"Submitting MFA code: {last_code}")
        response = self.session.post("https://login.scouting.nl/2fa_check", data = {
            '_auth_code': last_code,
        })
        contents = BeautifulSoup(response.content, "html.parser")
        self.endStep(self.check_title(contents, 'Scouts Online '))


    def accept_export_terms(self):
        self.nextStep('Accepting export terms')
        response = self.session.post("https://sol.scouting.nl/support/filter/export", data = {
            'redirectURI': 'https://sol.scouting.nl',
            'support_ok_with_export_terms': '',
            'support_ok_with_export_terms[1]': '1',
            'submitBtn': 'Download'
        })
        result = response.status_code
        self.endStep(result == 200)


    def clean_up(self):
        self.nextStep('Cleaning up')
        # ???
        self.printOk()
        print(f"{c.GREEN}Succesvol {self.current_step} stappen voltooid!{c.NC}")
