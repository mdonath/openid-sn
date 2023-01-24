import os
import requests

from sol_export.AnsiColors import AnsiColors as c


class Stepper:

    def __init__(self, hit_config):
        self.current_step = 0
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

    def next_step(self, description: str):
        self.current_step = self.current_step + 1
        print(f"{c.YELLOW}Step {self.current_step}:{c.NC} {description}...",
              end=' ', flush=True)

    def print_ok(self):
        print(f"[{c.GREEN}OK{c.NC}]\n")

    def print_fail(self):
        print(f"[{c.RED}FAIL{c.NC}]\n")

    def end_step(self, status: bool, msg: str = ''):
        if status:
            self.print_ok()
        else:
            self.print_fail()
            raise Exception('step failed ' + msg)

    def start_up(self, msg):
        stripes = "-"*len(msg)
        print(f"{stripes}\n{c.GREEN}{msg}{c.NC}\n{stripes}\n")

    def clean_up(self):
        self.next_step('Cleaning up')
        # ???
        self.print_ok()
        print(f"{c.GREEN}Succesvol {self.current_step} stappen voltooid!{c.NC}")
