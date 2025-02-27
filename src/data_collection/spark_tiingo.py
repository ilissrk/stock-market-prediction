from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pymongo import MongoClient

spark = SparkSession.builder \
    .appName("KafkaConsumer") \
    .master("local[*]") \
    .getOrCreate()

schema = StructType([
    StructField("date", StringType(), True),
    StructField("close", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("open", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("adjClose", DoubleType(), True),
    StructField("adjHigh", DoubleType(), True),
    StructField("adjLow", DoubleType(), True),
    StructField("adjOpen", DoubleType(), True),
    StructField("adjVolume", DoubleType(), True),
    StructField("divCash", DoubleType(), True),
    StructField("splitFactor", DoubleType(), True)
])

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["financial_data"]
mongo_collection = mongo_db["stock_prices"]

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tst") \
    .load()

df_parsed = df.select(from_json(col("value").cast("string"), schema).alias("data"))


df_selected = df_parsed.select(col("data.date").alias("date"), col("data.close").alias("close"))

def write_to_mongo(batch_df, batch_id):
    batch_data = batch_df.collect()
    for row in batch_data:
        mongo_collection.insert_one({"date": row["date"], "close": row["close"]})


query = df_selected.writeStream \
    .foreachBatch(write_to_mongo) \
    .outputMode("append") \
    .start()

query.awaitTermination()
