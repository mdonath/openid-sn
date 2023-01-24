#!/usr/bin/env python3

import yaml
from ki_import import UploadDeelnemersAantallen

if __name__ == "__main__":
    # laad configuratie
    credentials = yaml.safe_load(open("credentials.yaml"))['credentials']
    hit_config = yaml.safe_load(open("hit.yaml"))

    up = UploadDeelnemersAantallen(hit_config)
    special_value = up.set_up(credentials)
    up.upload()
    up.logout(special_value)
    up.clean_up()
