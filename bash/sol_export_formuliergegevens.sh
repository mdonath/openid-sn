#!/bin/bash

# Requires:
# - curl 7.68.0
# - tidy 5.6.0
# - xmlstarlet 1.6.1


FORM_ID=$1
USERNAME=$2
PASSWORD=$3
HIT_YEAR=$4


# 1000 - Deelnemer staat ingeschreven
# 1008 - Op wachtlijst
# 1020 - Ingeschreven, moet nog iDEAL-betaling
PARTICIPANT_STATUS="&prt_st_id[]=1000,1020,1008"


# Colors
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

OPENIDURL=https://login.scouting.nl/user/$USERNAME
COOKIE_JAR=cookies
OUTPUT_DIR=hit-${HIT_YEAR}


OPTIONS_CURL="--show-error --silent --location --user-agent 'Mozilla/5.0' --cookie $COOKIE_JAR --cookie-jar $COOKIE_JAR"
OPTIONS_TIDY="-indent -wrap -quiet -asxml -numeric -file /dev/null"
OPTIONS_XML="sel --text --template"


printf "${YELLOW}Step 1:${NC} Using login button..."
curl \
 $OPTIONS_CURL \
 --data "submitBtn=Log+in" \
 --url "https://sol.scouting.nl/rs/user/" \
| tidy $OPTIONS_TIDY > "step1.out"

TOKEN=`cat "step1.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='token']/@value" --value-of "."`
ASSOC_HANDLE=`cat "step1.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='openid.assoc_handle']/@value" --value-of "."`

#rm step1.out
printf " [${GREEN}OK${NC}]\n"
exit

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


printf "${YELLOW}Step 4:${NC} Finding linked forms for $FORM_ID..."
LINKED_FORMS=` \
curl \
 $OPTIONS_CURL \
 --url "https://sol.scouting.nl/as/form/$FORM_ID/report" \
| tidy -quiet -asxml -numeric -file /dev/null \
| xmlstarlet sel --text --template --match "//_:select[@name='linked_forms[]']//_:option/@value" --value-of "concat('&linked_forms[]=',.)"
`
printf " [${GREEN}OK${NC}]\n"

printf "${YELLOW}Step 5:${NC} Downloading formuliergegevens..."
curl \
 $OPTIONS_CURL \
 --data "button=part_data_linked&prt_st_id=$PARTICIPANT_STATUS&linked_forms=$LINKED_FORMS&submitBtn=submitBtn" \
 --output "$OUTPUT_DIR/formuliergegevens_$FORM_ID.csv" \
 --url "https://sol.scouting.nl/as/form/$FORM_ID/report"
printf " [${GREEN}OK${NC}]\n"

printf "${YELLOW}Step 6:${NC} Downloading subgroepen..."
curl \
 $OPTIONS_CURL \
 --data "button=team_data_linked&prt_st_id=$PARTICIPANT_STATUS&linked_forms=$LINKED_FORMS&submitBtn=submitBtn" \
 --output "$OUTPUT_DIR/subgroepen_$FORM_ID.csv" \
 --url "https://sol.scouting.nl/as/form/$FORM_ID/report"
printf " [${GREEN}OK${NC}]\n"


printf "${YELLOW}Step 8:${NC} Cleaning up..."
rm $COOKIE_JAR
printf " [${GREEN}OK${NC}]\n"

