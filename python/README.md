Dit zijn scripts om de inschrijfaantallen te downloaden uit SOL en te importeren op de website van de HIT.

# Stappen om het werkend te krijgen:
- Installeer een schone Raspberry Pi met de laatste Raspberry Pi OS, of iets anders met een scheduler en Python.
- Clone https://github.com/mdonath/openid-sn.git
- Ga naar directory `python`
- Kopieer `credentials-example.yaml` naar `credentials.yaml` en vul de gegevens in
- Run `crontab -e` en maak de volgende regel aan
  `59 6-23 * * * cd /home/pi/git/openid-sn/python && ./run.sh >> /home/pi/git/openid-sn/python/cron-output.log 2>&1`
  Het idee is dat tussen 7 en 24:00 de statistieken worden bijgewerkt. Omdat het met crontab lastig is om rond
  twaalf uur 's nachts iets te plannen heb ik als workaround ervoor gekozen om 23:59 als laatste te triggeren. Prima!

