#!/bin/bash

pushd `dirname $0` > /dev/null && CPATH=$(pwd) && popd > /dev/null                  # get path of script directory
echo "[$(date +'%F %r')] Login confirm:"
source $CPATH/config && \
curl -k -G -d mode=192 -d username=$USER -d a=$(($(date +%s)*1000)) $URL/live
