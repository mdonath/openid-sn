#!/bin/bash

# Requires:
# - curl 7.35.0
# - tidy 5.4.0
# - xmlstarlet 1.5.0

UPLOADFILE=$1
HITPROJECT=$2
USERNAME=$3
PASSWORD=$4

YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

OPENIDURL=https://login.scouting.nl/user/$USERNAME
COOKIE_JAR=cookies

OPTIONS_CURL="--show-error --silent --location --user-agent 'Mozilla/5.0' --cookie $COOKIE_JAR --cookie-jar $COOKIE_JAR"
OPTIONS_TIDY="-indent -wrap -quiet -asxml -numeric -file /dev/null"
OPTIONS_XML="sel --text --template"

rm -f $COOKIE_JAR

printf "${GREEN}IMPORTING FORMS INTO KAMPINFO${NC}\n"

#-------------------------
# STEP 1: Fetch login page
#-------------------------
printf "${YELLOW}Step 1:${NC} Fetching login-page..."
HIDDEN_FIELDS=`curl \
 $OPTIONS_CURL \
 --url "https://hit.scouting.nl/administrator/index.php" \
| tidy $OPTIONS_TIDY \
| xmlstarlet $OPTIONS_XML --match "//_:form[@id='form-login']//_:input[@type='hidden']" --value-of "concat('&',@name,'=',@value)"`
printf " [${GREEN}OK${NC}]\n"


#----------------------------
# STEP 2: Login with username
#----------------------------
printf "${YELLOW}Step 2:${NC} Using login button..."
curl \
 $OPTIONS_CURL \
 --data "username=${USERNAME}" \
 --data "passwd=" \
 --data "lang=" \
 --data "${HIDDEN_FIELDS}" \
 --url "https://hit.scouting.nl/administrator/index.php" \
| tidy $OPTIONS_TIDY > "step2.out"

RETURNTO=`cat "step2.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='openid.return_to']/@value" --value-of "."`
ASSOC_HANDLE=`cat "step2.out" | xmlstarlet $OPTIONS_XML --match "//_:form//_:input[@name='openid.assoc_handle']/@value" --value-of "."`

rm step2.out
printf " [${GREEN}OK${NC}]\n"
# echo "- returnto :  $RETURNTO"
# echo "- assoc_handle: $ASSOC_HANDLE"


#----------------------------------------
# STEP 3: Initiate login at OpenId server
#----------------------------------------
printf "${YELLOW}Step 3:${NC} Logging on $USERNAME at login.scouting.nl..."
TOKEN=`curl \
 $OPTIONS_CURL \
 --data "openid.ns=http://specs.openid.net/auth/2.0" \
 --data "openid.ns.sreg=http://openid.net/extensions/sreg/1.1" \
 --data "openid.sreg.required=email,fullname" \
 --data "openid.sreg.optional=language,timezone,nickname" \
 --data "openid.realm=https://hit.scouting.nl/administrator" \
 --data "openid.mode=checkid_setup" \
 --data "openid.return_to=${RETURNTO}" \
 --data "openid.identity=https://login.scouting.nl/user/${USERNAME}" \
 --data "openid.claimed_id=https://login.scouting.nl/user/${USERNAME}" \
 --data "openid.assoc_handle=$ASSOC_HANDLE" \
 --url "https://login.scouting.nl/provider/" \
| tidy $OPTIONS_TIDY \
| xmlstarlet $OPTIONS_XML --match "//_:form[@id='authenticate']//_:input[@name='token']" --value-of "@value"`
printf " [${GREEN}OK${NC}]\n"
#echo -TOKEN: ${TOKEN}


#-------------------------------
# STEP 4: Login at OpenId server
#-------------------------------
printf "${YELLOW}Step 4:${NC} Sending password for $USERNAME at login.scouting.nl..."
curl \
 $OPTIONS_CURL \
 --data "openid.ns=http://specs.openid.net/auth/2.0" \
 --data "openid.ns.sreg=http://openid.net/extensions/sreg/1.1" \
 --data "openid.sreg.required=email,fullname" \
 --data "openid.sreg.optional=language,timezone,nickname" \
 --data "openid.realm=https://hit.scouting.nl/administrator" \
 --data "openid.mode=checkid_setup" \
 --data-urlencode "openid.return_to=${RETURNTO}" \
 --data "openid.identity=https://login.scouting.nl/user/${USERNAME}" \
 --data "openid.claimed_id=https://login.scouting.nl/user/${USERNAME}" \
 --data "openid.assoc_handle=$ASSOC_HANDLE" \
 --data "token=${TOKEN}" \
 --data "retry_login=0" \
 --data-binary "password=${PASSWORD}" \
 --data "form_action=Inloggen" \
 --output "/dev/null" \
 --url "https://login.scouting.nl/provider/login/"
printf " [${GREEN}OK${NC}]\n"

#-------------------------
# STEP 5: Open import page
#-------------------------
printf "${YELLOW}Step 5:${NC} Opening import page, extracting special value"
SPECIALVALUE=`curl \
 $OPTIONS_CURL \
 --url "https://hit.scouting.nl/administrator/index.php?option=com_kampinfo&view=import" \
| tidy $OPTIONS_TIDY \
| xmlstarlet $OPTIONS_XML --match "//_:form[1]//_:input[@type='hidden' and @value='1']/@name" --value-of "."`
printf " [${GREEN}OK${NC}]\n"

# echo -SPECIALVALUE: $SPECIALVALUE


#--------------------
# STEP 6: Upload file
#--------------------
printf "${YELLOW}Step 6:${NC} Uploading file..."
curl \
 $OPTIONS_CURL \
 --form "option=com_kampinfo" \
 --form "view=import" \
 --form "task=import.importInschrijvingen" \
 --form "${SPECIALVALUE}=1" \
 --form "jform[jaar]=${HITPROJECT}" \
 --form "jform[import_inschrijvingen]=@\"${UPLOADFILE}\";type=text/csv" \
 --form "submit=Upload" \
 --output "result-upload.html" \
 --url "https://hit.scouting.nl/administrator/index.php"
printf " [${GREEN}OK${NC}]\n"

cat result-upload.html | grep "kampen gewijzigd met hun inschrijvingen"
rm result-upload.html


#-----------------
# STEP 7: Clean up
#-----------------
printf "${YELLOW}Step 7:${NC} Cleaning up..."
rm $COOKIE_JAR
#rm $UPLOADFILE
printf " [${GREEN}OK${NC}]\n"

