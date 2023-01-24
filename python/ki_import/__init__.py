import os
from time import sleep
from bs4 import BeautifulSoup

from sol_export.AnsiColors import AnsiColors as c
from sol_export.Stepper import Stepper


class UploadDeelnemersAantallen(Stepper):

    def __init__(self, hit_config):
        super().__init__(hit_config)
        self.start_up(
            f"IMPORTING FORMS INTO KAMPINFO - HIT {hit_config['current_year']}")

    def set_up(self, credentials):
        return self.login(credentials)

    def login(self, credentials):
        """
        Opent KampInfo
        """
        admin_page = "https://hit.scouting.nl/administrator/index.php"
        # open site
        self.next_step('Open HIT Admin')
        response = self.session.get(admin_page)
        contents = BeautifulSoup(response.content, "html.parser")
        hidden_fields = contents.find_all('input', {'type': 'hidden'})
        self.end_step(self.check_title(contents, 'HIT - Beheer'))

        # vul username in en druk op de inlogknop, password is hier niet nodig
        self.next_step('Login at HIT Admin')
        data = {hf['name']: hf['value'] for hf in hidden_fields}
        data.update(
            {
                'username': credentials['kampinfo']['username'],
                'passwd': credentials['kampinfo']['password'],
                'lang': ''
            }
        )
        response = self.session.post(url=admin_page, data=data)
        contents = BeautifulSoup(response.content, "html.parser")

        self.end_step(self.check_title(
            contents, 'Controlepaneel - HIT - Beheer'))

    def upload(self):
        # open import page
        self.next_step("Opening import page")
        response = self.session.get(
            "https://hit.scouting.nl/administrator/index.php?",
            params={
                'option': 'com_kampinfo',
                'view': 'import'
            }
        )
        contents = BeautifulSoup(response.content, "html.parser")
        special_value = contents.find_all(
            'input',
            {'type': 'hidden', 'value': '1'}
        )[0]['name']
        self.end_step(
            self.check_title(
                contents,
                'Import - HIT - Beheer') and len(special_value) > 0
        )

        # upload file
        self.next_step("Uploading file")
        input_dir = 'hit-2023/'
        file_name = '28405_formulieren.csv'
        if not os.path.exists(input_dir+file_name):
            raise Exception("Bestand kan niet gevonden worden")

        response = self.session.post(
            "https://hit.scouting.nl/administrator/index.php",
            data={
                'option': 'com_kampinfo',
                'view': 'import',
                'task': 'import.importInschrijvingen',
                special_value: '1',
                'jform[jaar]': f'{self.hit_config["current_year"]}',
                'submit': 'Upload',
            },
            files={
                'jform[import_inschrijvingen]': (
                    file_name,
                    open(input_dir + file_name, 'rb'),
                    'text/csv'
                )
            }
        )
        contents = BeautifulSoup(response.content, "html.parser")
        is_ok, msg = self.find_alert(contents)
        self.end_step(is_ok, msg)

        # Druk het resultaat nog even af
        print(msg)
        return special_value

    def find_alert(self, contents):
        alerts = contents.find_all('div', {'class': 'alert-message'})
        all = ' / '.join([div.contents[0] for div in alerts])
        pos = all.find('Er zijn nu')
        is_ok = pos >= 0
        msg = ''
        if is_ok:
            msg = all[pos:]
        else:
            msg = all
        return is_ok, msg

    def logout(self, special_value: str):
        self.next_step('Logout')
        url = 'https://hit.scouting.nl/administrator/index.php'
        response = self.session.get(
            url,
            params={
                'option': '=com_login',
                'task': 'logout',
                special_value: '1',
            }
        )
        self.end_step(response.status_code == 200)
