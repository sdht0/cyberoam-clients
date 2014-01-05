#!/bin/bash

pushd `dirname $0` > /dev/null && CPATH=$(pwd) && popd > /dev/null                  # get path of script directory
echo "[$(date +'%F %r')] Logging out..."
source $CPATH/config && \
curl -k  -d mode=193 -d username=$USER -d a=$(($(date +%s)*1000)) $URL/logout.xml && \
crontab -l | grep -v "$CPATH/confirm.sh" | crontab -                                # remove cron entry
