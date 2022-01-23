#!/bin/bash

USERNAME=$1
PASSWORD=$2
EVENT_ID=$3
HIT_YEAR=$4

# Download csv uit SOL
./sol_export_forms.sh ${EVENT_ID} ${USERNAME} ${PASSWORD}

# Toon aantal op display
./toon_totaal.sh ${EVENT_ID}_formulieren.csv

# upload csv naar KampInfo

#echo "SKIPPING UPLOAD NAAR KAMPINFO !!!"
./ki_import_forms.sh ${EVENT_ID}_formulieren.csv ${HIT_YEAR} ${USERNAME} ${PASSWORD}
