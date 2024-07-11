#!/bin/bash
echo ""
echo "== Running original KMeans implementation =="
time spark-submit Unit_7_KMeans_Original.py
echo ""
echo "== Running optimized KMeans implementation =="
time spark-submit Unit_7_KMeans_Optimized.py
