import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import save_model
from tiingo import TiingoClient
from datetime import datetime, timedelta


config = {
    'api_key': '8433d415662f088c87b2c935ccda3778e631c13f'  
}
client = TiingoClient(config)

ticker = 'AAPL'  
end_date = datetime.today()
start_date = end_date - timedelta(days=3 * 365)  

df_tiingo = client.get_dataframe(ticker, startDate=start_date, endDate=end_date)
df_tiingo.reset_index(inplace=True)
df_tiingo.rename(columns={"date": "created_format"}, inplace=True)

file_path_sentiment = 'apple_sentiment_scores.csv'  
df_sentiment = pd.read_csv(file_path_sentiment)

df_sentiment["created_format"] = pd.to_datetime(df_sentiment["created_format"])
df_tiingo["created_format"] = pd.to_datetime(df_tiingo["created_format"])

df_merged = pd.merge(df_sentiment, df_tiingo[["created_format", "close"]], on="created_format", how="inner")

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(df_merged[["sigmoid", "close"]])
data_normalized = pd.DataFrame(data_scaled, columns=["sigmoid_normalized", "close_normalized"])

def create_sequences(data, sequence_length):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i + sequence_length, :])  
        y.append(data[i + sequence_length, 1])   
    return np.array(X), np.array(y)

sequence_length = 30
X, y = create_sequences(data_scaled, sequence_length)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

model = Sequential()
model.add(LSTM(units = 50, activation = 'relu', return_sequences=True
              ,input_shape = (x_train.shape[1], 1)))
model.add(Dropout(0.2))


model.add(LSTM(units = 60, activation = 'relu', return_sequences=True))
model.add(Dropout(0.3))


model.add(LSTM(units = 80, activation = 'relu', return_sequences=True))
model.add(Dropout(0.4))


model.add(LSTM(units = 120, activation = 'relu'))
model.add(Dropout(0.5))

model.add(Dense(units = 1))
model.summary()
model.compile(optimizer='adam', loss='mse')

model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), verbose=1)

y_pred = model.predict(X_test)

y_test_rescaled = scaler.inverse_transform(
    np.concatenate((np.zeros((len(y_test), 1)), y_test.reshape(-1, 1)), axis=1)
)[:, 1]
y_pred_rescaled = scaler.inverse_transform(
    np.concatenate((np.zeros((len(y_pred), 1)), y_pred), axis=1)
)[:, 1]


rmse = np.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))


mape = mean_absolute_percentage_error(y_test_rescaled, y_pred_rescaled) * 100

# Print metrics
print(f"Root Mean Square Error (RMSE): {rmse:.2f}")
print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")

model.save('lstm_model.h5')
print("Modèle sauvegardé sous le nom 'lstm_model.h5'")

last_sequence = X_test[-1].reshape(1, sequence_length, X_test.shape[2])  
prediction = model.predict(last_sequence)

predicted_price = scaler.inverse_transform(
    np.concatenate((np.zeros((1, 1)), prediction), axis=1)
)[:, 1]

print(f"Prix prédit pour le jour suivant : {predicted_price[0]:.2f}")
