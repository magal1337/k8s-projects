from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import json
import logging
from  pyspark.sql.functions import input_file_name
#minio.storage-layer.svc.cluster.local:9000
conf = (
SparkConf()
    .set("spark.hadoop.fs.s3a.endpoint", "http://10.245.144.193:9000")
    .set("spark.hadoop.fs.s3a.access.key", "9TPEM7DXMUVP5WUWA21I")
    .set("spark.hadoop.fs.s3a.secret.key", "UPiPw9nhsGZ67R1smKF3ucClvMn9d1rwb9kUpNrY")
    .set("spark.hadoop.fs.s3a.path.style.access", True)
    .set("spark.hadoop.fs.s3a.fast.upload", True)
    .set("spark.hadoop.fs.s3a.connection.maximum", 100)
    .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .set("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore")
    .set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .set("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
)

# apply config
sc = SparkContext(conf=conf).getOrCreate()
if __name__ == '__main__':

    # init spark session
    # name of the app
    spark = SparkSession \
            .builder \
            .appName("sz-stock-analytics") \
            .getOrCreate()

    # set log level to info
    spark.sparkContext.setLogLevel("INFO")
    logging.basicConfig(level=logging.INFO)

    df = spark.read.csv("s3a://stock-market/lz/*.csv",header=True)
    df = df.withColumn("filename", input_file_name())
    df.createOrReplaceTempView("stocks")

    df_statistics = spark.sql("""
    WITH raw_data AS (
    SELECT
        CAST(timestamp AS TIMESTAMP) AS period,
        CAST(CAST(timestamp AS TIMESTAMP) AS DATE) AS day,
        FROM_UNIXTIME(UNIX_TIMESTAMP(timestamp),'H') AS hour,
        open,
        high,
        low,
        close,
        volume,
        REGEXP_EXTRACT(filename,"(?<=\/)[A-Z]+(?=-)",0) AS company
    FROM 
        stocks
    )
    SELECT * FROM raw_data
    """)

    df_statistics.write.format("delta").save("s3a://stock-market/bz/stock-market-summary")
    spark.stop()
