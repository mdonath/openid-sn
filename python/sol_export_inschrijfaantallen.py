#!/usr/bin/env python3

import yaml
from sol_export import DownloadInschrijvingen

if __name__ == "__main__":
    # laad configuratie
    credentials = yaml.safe_load(open("credentials.yaml"))['credentials']
    hit_config = yaml.safe_load(open("hit.yaml"))

    # download inschrijfaantallen voor KampInfo
    di = DownloadInschrijvingen(hit_config)
    di.set_up(credentials)
    di.download_inschrijvingen()
    di.clean_up()
