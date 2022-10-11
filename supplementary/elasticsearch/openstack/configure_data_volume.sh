#!/bin/bash
mkfs.xfs -L $(hostname -s) /dev/vdb
mkdir /data
echo "LABEL=$(hostname -s)       /data   xfs     defaults        0 0" >> /etc/fstab
mount /data
