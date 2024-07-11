from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark import SparkContext
import math
from collections import namedtuple
from time import time


# Number of clusters to find
K = 5
# Convergence threshold
THRESHOLD = 0.1
# Maximum number of iterations
MAX_ITERS = 20


def parse_coordinates(line):
    fields = line.split(',')
    return (float(fields[3]), float(fields[4]))


def distance(p1, p2):
    "Returns the squared distance between two given points"
    return (p1[0] - p2[0])** 2 + (p1[1] - p2[1])** 2


def closest_centroid(point, centroids):
    "Returns the index of the closest centroid to the given point: eg. the cluster this point belongs to"
    distances = [distance(point, c) for c in centroids]
    shortest = min(distances)
    return distances.index(shortest)


def add_points(p1, p2):
    "Returns the sum of two points"
    return (p1[0] + p2[0], p1[1] + p2[1])


if __name__ == '__main__':
    start = time()
    spark = SparkSession \
            .builder \
            .appName('KMeans Original') \
            .getOrCreate()
    sc = spark.sparkContext

    data = sc.textFile('datasets/locations')
    points = data.map(parse_coordinates)

    # Initial centroids: we just take K randomly selected points
    centroids = points.takeSample(False, K, 42)

    # Just make sure the first iteration is always run
    variation = THRESHOLD + 1
    iteration = 0

    while variation > THRESHOLD  and iteration < MAX_ITERS:
        # Map each point to (centroid, (point, 1))
        with_centroids = points.map(lambda p: (closest_centroid(p, centroids), (p, 1)))
        # For each centroid reduceByKey adding the coordinates of all the points
        # and keeping track of the number of points
        cluster_stats = with_centroids.reduceByKey(lambda (p1, n1), (p2, n2):  (add_points(p1, p2), n1 + n2))
        # For each existing centroid find the new centroid location calculating the average of each closest point
        new_centroids = cluster_stats.map(lambda (c, ((x, y), n)): (c, (x/n, y/n))).collect()
        # Calculate the variation between old and new centroids
        variation = 0
        for (old_centroid_id, new_centroid) in new_centroids:
            variation += distance(centroids[old_centroid_id], new_centroid)
        print('Variation in iteration {}: {}'.format(iteration, variation))
        # Replace old centroids with the new values
        for (old_centroid_id, new_centroid) in new_centroids:
            centroids[old_centroid_id] = new_centroid
        iteration += 1

    print('Final centroids: {}'.format(centroids))
    print('Elapsed time: {}'.format(time()-start))

    spark.stop()
