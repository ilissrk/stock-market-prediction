from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pymongo import MongoClient

from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch

model = BertForSequenceClassification.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis")
tokenizer = BertTokenizer.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis")

# Créer un pipeline
nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


spark = SparkSession.builder \
    .appName("KafkaConsumerReddit") \
    .master("local[*]") \
    .getOrCreate()
schema = StructType([
    StructField("score", DoubleType(), True)])

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["financial_data"]
mongo_collection = mongo_db["stock_prices"]

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "reddit-posts") \
    .load()


df_parsed = df.select(from_json(col("value").cast("string"), schema).alias("data"))
df_selected = df_parsed.select(col("data.title").alias("title"), col("data.score").alias("score"), col("data.sum_coin").alias("sum_coin"))

def apply_nlp(text):
    result = nlp(text)
    return result[0]['label']

# UDF (User-Defined Function) pour Spark
nlp_udf = udf(apply_nlp, StringType())

# Appliquer l'analyse NLP
df_with_sentiment = df_selected.withColumn("sentiment", nlp_udf(col("title")))

# Calculer le score global
def calculate_sentiment_score(ups, sum_coin, score, sentiment):
    overall_score = ups * 0.4 + sum_coin * 0.3 + score * 0.3
    if sentiment == "positive":
        overall_score *= 1
    elif sentiment == "negative":
        overall_score *= -1
    elif sentiment == "neutral":
        overall_score = 0
    return overall_score

# UDF pour calculer le score global
score_udf = udf(calculate_sentiment_score, DoubleType())

# Appliquer la fonction de calcul du score
df_with_scores = df_with_sentiment.withColumn(
    "overall_score",
    score_udf(col("ups"), col("sum_coin"), col("score"), col("sentiment"))
)

mean_score = df_final.agg({"overall_score": "mean"}).collect()[0][0]
# Calculer la fonction Sigmoid
def sigmoid(x):
    return 2 / (1 + np.exp(-x)) - 1

sigmoid_scoring = sigmoid(mean_score)

from time import datetime
today_date = datetime.now().strftime("%Y-%m-%d")
mongo_collection.update_one(
        {"date": today_date},
        {"$set": {"score": sigmoid_scoring}},
        upsert=False
    )