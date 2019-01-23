#!/bin/bash
HIERZO=`dirname "${BASH_SOURCE[0]}"`
cd $HIERZO

. CREDENTIALS
. HITCONFIG

./update_kampinfo.sh ${USERNAME} ${PASSWORD} ${EVENT_ID} ${HIT_YEAR}

