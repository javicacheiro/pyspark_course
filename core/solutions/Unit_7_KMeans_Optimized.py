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
    "Calculate the squared distance between two given points"
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def closest_centroid(point, centroidsBC):
    "Calculate the closest centroid to the given point: eg. the cluster this point belongs to"
    distances = [distance(point, c) for c in centroidsBC.value]
    shortest = min(distances)
    return distances.index(shortest)


def add_points(p1,p2):
    "Add two points of the same cluster in order to calculate later the new centroids"
    return [p1[0] + p2[0], p1[1] + p2[1]]


if __name__ == '__main__':
    start = time()
    spark = SparkSession \
            .builder \
            .appName('KMeans Optimized') \
            .getOrCreate()
    sc = spark.sparkContext

    data = sc.textFile('datasets/locations')
    points = data.map(parse_coordinates)
    points.cache()

    # Initial centroids: we just take K randomly selected points
    centroids = points.takeSample(False, K, 42)
    # Broadcast var
    centroidsBC = sc.broadcast(centroids)

    # Just make sure the first iteration is always run
    variation = THRESHOLD + 1
    iteration = 0

    while variation > THRESHOLD  and iteration < MAX_ITERS:
         # Map each point to (centroid, (point, 1))
        with_centroids = points.map(lambda p : (closest_centroid(p, centroidsBC), (p, 1)))
        # For each centroid reduceByKey adding the coordinates of all the points
        # and keeping track of the number of points
        cluster_stats = with_centroids.reduceByKey(lambda (p1, n1), (p2, n2):  (add_points(p1, p2), n1 + n2))
        # For each existing centroid find the new centroid location calculating the average of each closest point
        new_centroids = cluster_stats.map(lambda (c, ((x, y), n)): (c, [x/n, y/n])).collect()
        # Calculate the variation between old and new centroids
        variation = 0
        for  (c, point) in new_centroids:
            variation += distance(centroids[c], point)
        print('Variation in iteration {}: {}'.format(iteration, variation))
        # Replace old centroids with the new values
        for (c, point) in new_centroids:
            centroids[c] = point
        # Replace the centroids broadcast var with the new values
        centroidsBC = sc.broadcast(centroids)
        iteration += 1

    print('Final centroids: {}'.format(centroids))
    print('Elapsed time: {}'.format(time()-start))

    spark.stop()
