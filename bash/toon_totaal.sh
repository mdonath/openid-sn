#!/bin/bash

EXPORT=$1

TOTAAL=`awk 'BEGIN {FS="^\"|\",\"|\"$";} { sum+= $5} END {print sum}' $EXPORT`

# python ./print_display.py $TOTAAL

mosquitto_pub -h mqtt -t "scouting/hit/inschrijvingen/totaal" --retain -m "$TOTAAL"
