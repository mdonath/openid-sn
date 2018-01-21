#!/bin/bash

# Requires:
# - curl 7.35.0
# - tidy 5.4.0
# - xmlstarlet 1.5.0

EVT_ID=$1
USERNAME=$2
PASSWORD=$3

YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

OPENIDURL=https://login.scouting.nl/user/$USERNAME
COOKIE_JAR=cookies

OPTIONS_CURL="--show-error --silent --location --user-agent 'Mozilla/5.0' --cookie $COOKIE_JAR --cookie-jar $COOKIE_JAR"
OPTIONS_TIDY="-indent -wrap -quiet -asxml -numeric -file /dev/null"
OPTIONS_XML="sel --text --template"

printf "${GREEN}DOWNLOADING FORMS FROM Scouts Online${NC}\n"


printf "${YELLOW}Step 1:${NC} Using login button..."
curl \
 $OPTIONS_CURL \
 --data "submitBtn=Log+in" \
 --url "https://sol.scouting.nl/rs/user/" \
| tidy $OPTIONS_TIDY > "step1.out"

TOKEN=`cat "step1.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='token']/@value" --value-of "."`
ASSOC_HANDLE=`cat "step1.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='openid.assoc_handle']/@value" --value-of "."`

rm step1.out
printf " [${GREEN}OK${NC}]\n"
#echo "- Login-token :  $TOKEN"
#echo "- assoc_handle: $ASSOC_HANDLE"


printf "${YELLOW}Step 2:${NC} Logging on $USERNAME at login.scouting.nl..."
curl \
 $OPTIONS_CURL \
 --data "openid.ns=http://specs.openid.net/auth/2.0" \
 --data "openid.mode=checkid_setup" \
 --data "openid.identity=http://specs.openid.net/auth/2.0/identifier_select" \
 --data "openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select" \
 --data "openid.return_to=https://sol.scouting.nl/rs/user/?perform=loginDone" \
 --data "openid.realm=https://sol.scouting.nl/" \
 --data "openid.ns_theme=https://login.scouting.nl/ns/theme/1.0" \
 --data "openid.theme_theme=TC3_leaf" \
 --data "openid.assoc_handle=$ASSOC_HANDLE" \
 --data "token=$TOKEN" \
 --data-binary "username=$USERNAME" \
 --data-binary "password=$PASSWORD" \
 --data "form_action=Inloggen" \
 --output "/dev/null" \
 --url "https://login.scouting.nl/provider/authenticate"
printf " [${GREEN}OK${NC}]\n"


printf "${YELLOW}Step 3:${NC} Accepting export terms..."
curl \
 $OPTIONS_CURL \
 --data "redirectURI=https://sol.scouting.nl" \
 --data "support_ok_with_export_terms=" \
 --data "support_ok_with_export_terms[1]=1" \
 --data "submitBtn=Download" \
 --output "/dev/null" \
 --url "https://sol.scouting.nl/support/filter/export"
printf " [${GREEN}OK${NC}]\n"


printf "${YELLOW}Step 4:${NC} Downloading forms for event $EVT_ID..."
curl \
 $OPTIONS_CURL \
 --output "${EVT_ID}_formulieren.csv" \
 --url "https://sol.scouting.nl/as/event/${EVT_ID}/forms/?evt_id=${EVT_ID}&export=true"
printf " [${GREEN}OK${NC}]\n"


printf "${YELLOW}Step 5:${NC} Cleaning up..."
rm $COOKIE_JAR
printf " [${GREEN}OK${NC}]\n"

