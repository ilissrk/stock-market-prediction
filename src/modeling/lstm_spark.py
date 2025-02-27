from pyspark.sql import SparkSession
from pyspark.sql.functions import col, pandas_udf, struct
import tensorflow as tf
import numpy as np
from pyspark.sql.types import FloatType, TimestampType, StructType, StructField

spark = SparkSession.builder \
    .appName("Spark MongoDB LSTM Prediction") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/financial_data.stock_prices") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/financial_data.stock_prices") \
    .getOrCreate()

data_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()

data_df.printSchema()
data_df.show()


data_df = data_df.select("date", "close", "scoring").orderBy("date")

model = tf.keras.models.load_model("lstm_model.h5")


from sklearn.preprocessing import MinMaxScaler

def normalize_data(df):
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df)
    return scaler, df_scaled


data_pandas = data_df.toPandas()


close_values = data_pandas["close"].values.reshape(-1, 1)
scoring_values = data_pandas["scoring"].values.reshape(-1, 1)


scaler, data_scaled = normalize_data(np.hstack((scoring_values, close_values)))


sequence_length = 30

def create_sequences(data, sequence_length):
    sequences = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)

sequences = create_sequences(data_scaled, sequence_length)


predictions = model.predict(sequences)
predicted_close = scaler.inverse_transform(
    np.hstack((np.zeros((len(predictions), 1)), predictions))
)[:, 1]

predicted_dates = data_pandas["date"].values[sequence_length:]


schema = StructType([
    StructField("date", TimestampType(), True),
    StructField("predicted_close", FloatType(), True)
])

predicted_df = spark.createDataFrame(
    [(predicted_dates[i], float(predicted_close[i])) for i in range(len(predicted_close))],
    schema=schema
)

predicted_df.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()

print("Prédictions sauvegardées dans MongoDB, collection: financial_data.stock_prices")
