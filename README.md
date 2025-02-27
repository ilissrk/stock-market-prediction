# Real-Time Stock Market Prediction Using Sentiment Analysis


## 📊 Project Overview

This project implements a sophisticated real-time stock market prediction system that analyzes sentiment from social networks (Reddit) alongside traditional financial data (Tiingo) to forecast stock price movements. By combining social media sentiment with market data, we aim to capture both quantitative factors and market sentiment that influence stock prices.

## 🚀 Key Features

- **Real-time data processing** using Apache Kafka and Spark Streaming
- **Sentiment analysis** of social media posts related to specific stocks
- **Advanced prediction models** using LSTM neural networks
- **Scalable architecture** with containerized components
- **Interactive visualizations** through Power BI dashboards

## 🏗️ Architecture

The system follows a modular big data pipeline architecture:

1. **Data Collection Layer**
   - Reddit data collection (social sentiment)
   - Tiingo financial API integration (market data)
   - Scheduled extraction via Apache Airflow

2. **Processing Layer**
   - Apache Kafka for message queueing
   - Apache Spark for stream processing
   - Sentiment analysis and feature extraction

3. **Storage Layer**
   - MongoDB for storing processed data
   - Scalable document storage

4. **Analysis & Prediction Layer**
   - LSTM neural networks for time-series prediction
   - Combined sentiment-financial analysis

5. **Visualization Layer**
   - Power BI dashboards
   - Real-time monitoring interfaces

## 🛠️ Technology Stack

- **Data Collection**: Python, Reddit API, Tiingo API, Apache Airflow
- **Data Processing**: Apache Kafka, Apache Spark, PySpark
- **Machine Learning**: TensorFlow/Keras, LSTM Networks, Scikit-learn
- **Data Storage**: MongoDB
- **Containerization**: Docker
- **Visualization**: Power BI
- **Orchestration**: Apache Airflow

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Access to Reddit API (credentials)
- Tiingo API key
- MongoDB instance
- Apache Kafka and Zookeeper
- Apache Spark

## 🔧 Installation & Setup

### Clone the repository

```bash
git clone https://github.com/yourusername/stock-market-prediction.git
cd stock-market-prediction
```

### Environment setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with your API credentials:

```
# .env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=your_app_name
TIINGO_API_KEY=your_tiingo_api_key
MONGODB_CONNECTION_STRING=your_mongodb_connection_string
```

### Docker setup

```bash
# Start the entire stack
docker-compose up -d
```

## 🚦 Running the Pipeline

### 1. Start data collection

```bash
# Start Airflow to orchestrate data collection
docker-compose up -d airflow

# Or manually trigger collection
python src/data_collection/retreive.py
python src/data_collection/spark_tiingo.py
```

### 2. Process data streams

```bash
# Start Kafka and Spark processing
docker-compose up -d kafka spark

# Or run processing scripts directly
python src/processing/spark_scoring_sentiment.py
```

### 3. Train and deploy the model

```bash
# Train LSTM model
python src/modeling/lstm_train.py

# Deploy for predictions
python src/modeling/lstm_spark.py
```

## 📊 Visualization

After running the pipeline, access the visualization through:

1. Power BI dashboard (import connection settings from `config/powerbi_settings.json`)
2. Web interface (if implemented): http://localhost:8080

## 📂 Project Structure

```
stock-market-prediction/
├── data/                        # Data storage (gitignored)
├── docs/                        # Documentation
│   └── project_report.pdf       # Detailed project report
├── notebooks/                   # Jupyter notebooks
│   ├── score_creation_training.ipynb
│   └── sentiment_scoring_training.ipynb
├── src/                         # Source code
│   ├── data_collection/         # Data collection scripts
│   │   ├── retreive.py          # Reddit data collection
│   │   └── spark_tiingo.py      # Financial data collection
│   ├── processing/              # Data processing scripts
│   │   └── spark_scoring_sentiment.py  # Sentiment analysis
│   └── modeling/                # ML modeling scripts
│       ├── lstm_spark.py        # LSTM with Spark integration
│       └── lstm_train.py        # LSTM model training
├── config/                      # Configuration files
│   ├── kafka_config.json
│   └── mongodb_config.json
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## 📝 Usage Examples

### Collecting Reddit data for a specific stock

```python
from src.data_collection.retreive import RedditCollector

collector = RedditCollector()
tesla_data = collector.collect_posts('TSLA', subreddit='wallstreetbets', limit=100)
```

### Running sentiment analysis

```python
from src.processing.spark_scoring_sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
sentiment_scores = analyzer.process_batch('AAPL')
```

### Making predictions

```python
from src.modeling.lstm_train import StockPredictor

predictor = StockPredictor(model_path='models/lstm_model.h5')
tomorrow_prediction = predictor.predict('AAPL')
```

## 🔍 Results and Performance

Our LSTM model, enhanced with sentiment analysis features, achieved:

- **Mean Absolute Error (MAE)**: 0.42
- **Root Mean Square Error (RMSE)**: 0.65
- **Directional Accuracy**: 68.5%

For more detailed analysis, refer to the full project report in the `docs` directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Iliass Rafk - iliassrafikpro@gmail.com

Project Link: [https://github.com/yourusername/stock-market-prediction](https://github.com/yourusername/stock-market-prediction)

## 🙏 Acknowledgements

- [Reddit API](https://www.reddit.com/dev/api/)
- [Tiingo API](https://api.tiingo.com/)
- [Apache Kafka](https://kafka.apache.org/)
- [Apache Spark](https://spark.apache.org/)
- [TensorFlow](https://www.tensorflow.org/)
