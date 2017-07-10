from __future__ import print_function
from pyspark import SparkContext
from pyspark.sql import Row, HiveContext


def parse_row(line):
    """Convert a line into a Row"""
    # All data lines start with 6 spaces
    if line.startswith('      '):
        codigo = int(line[:17].strip())
        datahora = line[17:40]
        data, hora = datahora.split()
        parametro = line[40:82].strip()
        valor = float(line[82:].replace(',', '.'))
        return [Row(codigo=codigo, data=data, hora=hora, parametro=parametro, valor=valor)]
    return []


if __name__ == '__main__':
    sc = SparkContext(appName='Meteo analysis')
    sqlContext = HiveContext(sc)
    rdd = sc.textFile('datasets/meteogalicia.txt')
    data = rdd.flatMap(parse_row).toDF()
    count = data.count()
    print('Total count:', count)
    t = data.where(data.parametro.like('Temperatura media %'))
    print('Maximum temperature')
    t.groupBy().max('valor').show()
    print('Minimum temperature')
    t.where(t.codigo == 1).groupBy().min('valor').show()
    print('Average temperatures per day')
    t.groupBy(t.data).mean('valor').sort('data').show(30)
    sc.stop()
