#!/bin/bash
TMPDIR=$(mktemp -d)
git clone --depth=1 git@github.com:javicacheiro/pyspark_course.git $TMPDIR/notebooks
cd $TMPDIR
tar czvf notebooks.tar.gz notebooks

echo "You can find the packaged notebooks at: $TMPDIR/notebooks.tar.gz"
