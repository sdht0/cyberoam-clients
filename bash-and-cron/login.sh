#!/bin/bash

pushd `dirname $0` > /dev/null && CPATH=$(pwd) && popd > /dev/null                  # get path of script directory
crontab -l | grep -v "$CPATH/confirm.sh" | crontab -                                # remove any earlier cron entry
echo "[$(date +'%F %r')] Logging in..."
source $CPATH/config && \
curl -k -d mode=191 -d username=$USER -d password=$PASSWORD -d a=$(($(date +%s)*1000)) $URL/login.xml && \
(crontab -l; echo "*/3 * * * * $CPATH/confirm.sh >> $CPATH/curl.log 2>&1") | crontab -
