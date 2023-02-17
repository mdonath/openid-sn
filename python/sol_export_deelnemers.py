#!/usr/bin/env python3

import yaml
from sol_export import DownloadDeelnemers

if __name__ == "__main__":
    # laad configuratie
    credentials = yaml.safe_load(open("credentials.yaml"))['credentials']
    hit_config = yaml.safe_load(open("hit.yaml"))

    # download deelnemer details
    dd = DownloadDeelnemers(hit_config)
    dd.set_up(credentials)
    dd.download_alle_deelnemers()
    dd.clean_up()
