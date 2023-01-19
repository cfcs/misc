#!/usr/bin/env bash

tgtmac=12:34:56:78:9a:bc
# where 12:34:56:78:9a:bc is the addr of the bluetooth boombox playing
# crypto currency podcasts at deafening volumes when you're trying to sleep

#$cat /storage/.config/system.d/fuck-off-cryptobro.service
#Description=Fuck off cryptobro
#[Service]
#Type=simple
#ExecStart=/storage/silence-bluetooth.sh
#Restart=always
#RestartSec=30
#[Install]
#WantedBy=multi-user.target

ping10()
{
  l2test -T -M -s -m -p $tgtmac &> /dev/null
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  l2ping $tgtmac || \
  return 1
}
while true
do
  until ping10 &>/dev/null; do sleep 300; done
  echo contact with $tgtmac, starting connect sequence
  while ping10
  do
    for i in $(seq 20000)
    do
      l2test -T -M -s -m -p $tgtmac &> /dev/null
    done
  done
done
