from sol_export.AnsiColors import AnsiColors as c


class Stepper:

    def __init__(self):
        self.current_step = 0

    def nextStep(self, description: str):
        self.current_step = self.current_step + 1
        print(f"{c.YELLOW}Step {self.current_step}:{c.NC} {description}...", end=' ', flush=True)

    def printOk(self):
        print(f"[{c.GREEN}OK{c.NC}]\n")

    def printFail(self):
        print(f"[{c.RED}FAIL{c.NC}]\n")

    def endStep(self, status: bool):
        if status:
            self.printOk()
        else:
            self.printFail()