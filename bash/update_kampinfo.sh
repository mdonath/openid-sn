#!/bin/bash

USERNAME=$1
PASSWORD=$2

# Download csv uit SOL
./sol_export_forms.sh 7239 $USERNAME $PASSWORD

# upload csv naar KampInfo
./ki_import_forms.sh 7239_formulieren.csv 2018 $USERNAME $PASSWORD

