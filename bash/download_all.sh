#!/bin/bash

. CREDENTIALS
. HITCONFIG

for form_id in ${FORM_BASIS_ID} ${FORM_OUDERKIND_ID}
do
    ./sol_export_formuliergegevens.sh ${form_id} "${USERNAME}" "${PASSWORD}"
done

