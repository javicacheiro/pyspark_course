#!/bin/bash
TMPDIR=$(mktemp -d)
mkdir $TMPDIR/notebooks
cp -a ../pyspark_course/README.md ../pyspark_course/*.ipynb ../pyspark_course/exercises/ ../pyspark_course/solutions/ $TMPDIR/notebooks
cd $TMPDIR
tar czvf notebooks.tar.gz notebooks

echo "You can find the packaged notebooks at: $TMPDIR/notebooks.tar.gz"
