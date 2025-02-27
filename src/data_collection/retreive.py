from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import praw
import json
import six
import sys
import pandas as pd
import requests
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves

from kafka import KafkaProducer

# Function for scraping Reddit
def scrap_reddit():
    print("done")
    try:
        # Kafka producer setup
        producer = KafkaProducer(
            bootstrap_servers='broker:29092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Reddit API setup
        reddit = praw.Reddit(
            client_id="S6M3St3xzoPKX1nfajz1Ug",
            client_secret="NLNa_A8dtRC7tsP6PxBE70oWxUVyTg",
            user_agent="sentiment_analyse (by u/zedon77)"
        )

        keywords = ["Tesla", "TSLA", "Nvidia", "NVDA", "Apple", "AAPL"]
        subreddits = ["stocks", "investing", "wallstreetbets", "finance"]
        post_limit = 50
        keyword_data = {"Tesla": [], "Nvidia": [], "Apple": []}

        for subreddit in subreddits:
            print(f"\n📊 Scraping subreddit: r/{subreddit}")
            for keyword in keywords:
                print(f"\n🔍 Searching for: {keyword}")
                for post in reddit.subreddit(subreddit).search(keyword, limit=post_limit):
                    post_data = {
                        "title": post.title,
                        "created_date": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                        "ups": post.ups,
                        "link_flair_text": post.link_flair_text,
                        "sum_coin": post.total_awards_received,
                        "score": post.score,
                    }
                    if keyword in ["Tesla", "TSLA"]:
                            keyword_data["Tesla"].append(post_data)
                    elif keyword in ["Nvidia", "NVDA"]:
                            keyword_data["Nvidia"].append(post_data)
                    elif keyword in ["Apple", "AAPL"]:
                            keyword_data["Apple"].append(post_data)

                    # Send to Kafka
                    producer.send('reddit_posts', post_data)
                    print(f"✅ Sent to Kafka: {post_data}")
                    print("-" * 50)

        # Close Kafka producer
        # for keyword, data in keyword_data.items():
        #     df = pd.DataFrame(data)
        #     csv_filename = f"{keyword.lower()}.csv"
        #     df.to_csv(csv_filename, index=False)
        #     print(f"📁 Data saved to {csv_filename}")

        producer.close()
        
    except Exception as e:
        print(f"Error during Reddit scraping or Kafka communication: {e}")
TIINGO_API_KEY = '8433d415662f088c87b2c935ccda3778e631c13f'
TIINGO_URL = "https://api.tiingo.com/tiingo/daily/{ticker}/prices"

KAFKA_BROKER = 'broker:29092'
TOPIC_NAME = 'tiiingo'

def fetch_tiingo_data(ticker):
    """Récupère les données de Tiingo pour un ticker donné à la date actuelle."""
    headers = {'Content-Type': 'application/json', 'Authorization': f'Token {TIINGO_API_KEY}'}
    today = datetime.now().strftime('%Y-%m-%d')  # Date actuelle
    params = {
        'startDate': today,
        'endDate': today
    }
    response = requests.get(TIINGO_URL.format(ticker=ticker), headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur: {response.status_code}, {response.text}")
        return None

def produce_data():
    """Envoie des données Tiingo pour AAPL vers Kafka."""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    ticker = 'AAPL'  # Ticker à surveiller
    data = fetch_tiingo_data(ticker)
    if data:
        print(f"Envoi des données pour {ticker} : {data}")
        producer.send(TOPIC_NAME, value=data)



def scrap_tiingo():
    produce_data()
    

# Airflow DAG setup
default_args = {
    'owner': 'nou',  
    'start_date': datetime(2023, 1, 1)
}

with DAG(   
    dag_id='scrap_posts',
    default_args=default_args,
    schedule='0 18-23,0-8 * * 1-5',  # Run every hour
    catchup=False,
) as dag:

       

    hello_task = PythonOperator(
        task_id='reddit',
        python_callable=scrap_reddit,
    )
with DAG(   
    dag_id='scrap_tiingo',
    default_args=default_args,
    schedule_interval='@daily',  # Exécution quotidienne
    start_date=datetime(2025, 1, 15, 18, 0),  # Commence à 18h # Run every hour
    catchup=False,
) as dag:

       

    hello_task = PythonOperator(
        task_id='tiingo',
        python_callable=scrap_tiingo,
    )

