#!/usr/bin/env python3
# encoding: utf-8
import sys
import re
import json
import pandas as pd

INDEX_NAME = 'movies'

if len(sys.argv) != 2:
    print('Please provide the name of the input file')

filename = sys.argv[1]

# title contains the name of the film and the year
# eg. Toy Story (1995)
pattern = re.compile(r'(.*) \((\d+)\)')

df = pd.read_csv(filename)
for index, row in df.iterrows():
    movieId = row['movieId']
    m = pattern.match(row['title'])
    if m:
        title = m.group(1)
        year = m.group(2)
    else:
        title = row['title']
        year = None
    genres = row['genres'].split('|')
    create = {"create": {"_index": INDEX_NAME, "_id": movieId}}
    movie = {"movieId": movieId, "title": title, "year": year, "genres": genres}
    print(json.dumps(create))
    print(json.dumps(movie))
