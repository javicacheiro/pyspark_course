#!/bin/bash
rsync -av --exclude=".*" --exclude="sync.sh" --exclude="clean.sh" --dry-run ./ /opt/cesga/cursos/pyspark_2021/

echo "This was run only in dry-run mode!!"
echo "If it does what you want run the rsync command manually"
