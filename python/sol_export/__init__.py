from bs4 import BeautifulSoup

from sol_export.SolStepper import SolStepper


__all__ = ["DownloadDeelnemers", "DownloadInschrijvingen"]


class DownloadDeelnemers(SolStepper):

    def __init__(self, hit_config):
        super().__init__(hit_config)


    def download_alle_deelnemers(self):
        for form_id in self.hit['forms']:
            self.download_deelnemers(form_id)


    def download_deelnemers(self, form_id):
        self.nextStep(f"Finding linked forms for {form_id}")
        response = self.session.get(f"https://sol.scouting.nl/as/form/{form_id}/report")
        contents = BeautifulSoup(response.content, "html.parser")
        linked_forms_ids = [option['value'] for option in contents.find('select', attrs = {'name': 'linked_forms[]'}).find_all('option') ]
        self.printOk()
        #print(linked_forms_ids)

        self.nextStep(f'Downloading formuliergegevens of {len(linked_forms_ids)} forms')
        response = self.session.post(
            f"https://sol.scouting.nl/as/form/{form_id}/report",
            {
                'button': 'part_data_linked',
                'prt_st_id[]': self.hit['participant_status'],
                'linked_forms[]': linked_forms_ids,
                'submitBtn': 'submitBtn'
            }
        )
        with open(f"{self.output_dir}/formuliergegevens_{form_id}.csv", "w") as fo:
            fo.write(response.text)
        self.printOk()


        self.nextStep('Downloading corresponding subgroepen')
        response = self.session.post(
            f"https://sol.scouting.nl/as/form/{form_id}/report",
             {
                'button': 'team_data_linked',
                'prt_st_id[]': self.hit['participant_status'],
                'linked_forms[]': linked_forms_ids,
                'submitBtn': 'submitBtn'
            }
        )
        with open(f"{self.output_dir}/subgroepen_{form_id}.csv", "w") as fo:
            fo.write(response.text)
        self.printOk()


class DownloadInschrijvingen(SolStepper):

    def __init__(self, hit_config):
        super().__init__(hit_config)

    def download_inschrijvingen(self):
        r"""Haalt via een GET het oerzicht met alle inschrijf-aantallen op.
        """
        event_id = self.hit['event_id']

        self.nextStep(f'Downloading forms for event {event_id}')
        response = self.session.get(f"https://sol.scouting.nl/as/event/{event_id}/forms",
            params = {
            'evt_id': event_id,
            'export': 'true'
            },
            stream = True,
        )

        with open(f"{self.output_dir}/{event_id}_formulieren.csv", "wb") as fo:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fo.write(chunk)
        self.endStep(True)
