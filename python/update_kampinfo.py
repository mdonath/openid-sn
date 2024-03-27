#!/usr/bin/env python3

import yaml
from sol_export import DownloadInschrijvingen
from ki_import import UploadDeelnemersAantallen


if __name__ == "__main__":
    # laad configuratie
    credentials = yaml.safe_load(open("credentials.yaml"))['credentials']
    hit_config = yaml.safe_load(open("hit.yaml"))

    # download inschrijfaantallen uit SOL
    down = DownloadInschrijvingen(hit_config)
    down.set_up(credentials)
    down.download_inschrijvingen()
    down.clean_up()

    # upload naar KampInfo
    up = UploadDeelnemersAantallen(hit_config)
    special_value = up.set_up(credentials)
    up.upload()
    up.logout(special_value)
    up.clean_up()

