from __future__ import print_function
from pyspark import SparkContext


def parse_temperature(line):
    (_, date, hour, _, _, _, value) = line.split()
    return (date, float(value.replace(',', '.')))


def sum_pairs(a, b):
    return (a[0]+b[0], a[1]+b[1])


if __name__ == '__main__':
    sc = SparkContext(appName='Meteo analysis')

    rdd = sc.textFile('datasets/meteogalicia.txt')

    temperatures = (rdd.filter(lambda line: 'Temperatura media' in line)
                    .map(parse_temperature))

    averages = (temperatures.map(lambda (date, t): (date, (t, 1)))
                .reduceByKey(sum_pairs)
                .mapValues(lambda (temp, count): temp/count))

    result = averages.sortByKey().collect()
    print('Average temperature per day')
    for date, temp in result:
        print('{} {}'.format(date, temp))

    sc.stop()
