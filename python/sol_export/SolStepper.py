from bs4 import BeautifulSoup

import sol_mfa

from sol_export.AnsiColors import AnsiColors as c
from sol_export.Stepper import Stepper


class SolStepper(Stepper):

    def __init__(self, hit_config):
        super().__init__(hit_config)

    def set_up(self, credentials):
        self.login(credentials)
        self.accept_export_terms()

    def login(self, credentials):
        csrf_token = self.step_open_site(credentials)
        self.step_login_at_loginserver(credentials, csrf_token)
        last_code = self.step_retrieve_mfa_code(credentials)
        self.step_submit_mfa_code(last_code, 'Scouts Online ')

    def step_open_site(self, credentials):
        """
        Opent de website en gaat naar het inloggen bij Scouting Nederland
        """

        # open site
        self.next_step('Open Scouts Online')
        response = self.session.get('https://sol.scouting.nl')
        contents = BeautifulSoup(response.content, "html.parser")
        token = contents.find_all('input', {'name': 'token'})[0]['value']
        self.end_step(self.check_title(contents, 'Scouts Online '))

        # druk op de inlogknop om naar de inlogserver te gaan
        self.next_step('Using login button')
        response = self.session.post("https://sol.scouting.nl/rs/user/", data={
            'token': token,
            'submitBtn': 'Log+in'
        })
        contents = BeautifulSoup(response.content, "html.parser")
        inputs = {n['name']: (n['value'] if n.has_attr('value') else None)
                  for n in contents.find_all('input')}

        csrf_token = inputs['login[_csrf_token]']
        self.end_step(self.check_title(
            contents, 'Inloggen bij Scouting Nederland') and len(csrf_token) > 0)
        return csrf_token

    def step_login_at_loginserver(self, credentials, csrf_token):
        """
        Vult username en password in, neemt ook csrf_token mee
        """
        self.next_step(
            f"Logging on {credentials['sol']['username']} at login.scouting.nl")

        response = self.session.post("https://login.scouting.nl/provider/authenticate", data={
            'login[username]': credentials['sol']['username'],
            'login[password]': credentials['sol']['password'],
            'login[_csrf_token]': csrf_token,
            'login[email_repeat]': '',
        })
        contents = BeautifulSoup(response.content, "html.parser")

        self.end_step(self.check_title(
            contents, 'Multifactor authenticatie code invoeren'))

    def step_retrieve_mfa_code(self, credentials):
        """
        Haalt de mfa-code op uit Gmail.
        """
        self.next_step(f"Retrieving MFA code from gmail")
        last_code = sol_mfa.get_mfa_token_from_mailbox(
            credentials['gmail']['username'],
            credentials['gmail']['password'],
            credentials['gmail']['folder']
        )
        self.end_step(last_code != None)
        return last_code

    def step_submit_mfa_code(self, last_code, title):
        """
        Vult de mfa-code in op het inlogscherm.
        """
        self.next_step(f"Submitting MFA code: {last_code}")
        response = self.session.post("https://login.scouting.nl/2fa_check", data={
            '_auth_code': last_code,
        })
        contents = BeautifulSoup(response.content, "html.parser")
        self.end_step(self.check_title(contents, title))

    def accept_export_terms(self):
        self.next_step('Accepting export terms')
        response = self.session.post("https://sol.scouting.nl/support/filter/export", data={
            'redirectURI': 'https://sol.scouting.nl',
            'support_ok_with_export_terms': '',
            'support_ok_with_export_terms[1]': '1',
            'submitBtn': 'Download'
        })
        result = response.status_code
        self.end_step(result == 200)
