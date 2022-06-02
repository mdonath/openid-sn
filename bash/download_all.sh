#!/bin/bash

. CREDENTIALS
. HITCONFIG

for form_id in ${FORM_BASIS_ID} ${FORM_OUDERKIND1_ID} ${FORM_OUDERKIND2_ID}
do
    ./sol_export_formuliergegevens.sh ${form_id} "${USERNAME}" "${PASSWORD}" "${HIT_YEAR}"
done

