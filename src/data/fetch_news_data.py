import os
import requests
import pandas as pd
from datetime import datetime
from transformers import pipeline

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)

API_KEY = "ee1cc13b03fc4897bf335dd559a39a6d"
url = "https://newsapi.org/v2/everything"

pipe = pipeline("text-classification",
                model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")


def fetch_articles(query, from_date, to_date, api_key):
    params = {
        'q': query,
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'apiKey': api_key
    }
    response = requests.get(url, params=params)
    return response.json()


def analyze_sentiments(articles):
    sentiments = []
    for article in articles:
        published_date = article.get('publishedAt', '')[:10]
        try:
            date_obj = datetime.strptime(published_date, '%Y-%m-%d').date()
            if date_obj >= datetime.strptime('2024-05-23', '%Y-%m-%d').date():
                sentiment = pipe(article['title'])[0]['label']
                sentiments.append({
                    'date': published_date,
                    'sentiment_score': 1 if sentiment == 'positive' else (-1 if sentiment == 'negative' else 0),
                    'url': article['url']
                })
        except ValueError:
            continue
    return sentiments


def save_aggregated_sentiments(sentiments, filename):
    df = pd.DataFrame(sentiments)
    if os.path.isfile(filename):
        existing_data = pd.read_csv(filename)
        # Filter out existing articles from aggregated data
        new_data = df[~df['url'].isin(existing_data['url'])]
        # Append only new articles
        updated_data = pd.concat([existing_data, new_data])
    else:
        updated_data = df

    updated_data = updated_data.sort_values(by='date')
    updated_data.to_csv(filename, index=False)
    print(f"Aggregated sentiment data saved to {filename}")


if __name__ == "__main__":
    from_date = "2024-05-23"
    to_date = datetime.today().date().isoformat()
    queries = ["gold price", "stock market"]

    all_articles = []
    for query in queries:
        articles = fetch_articles(query, from_date, to_date, API_KEY)
        all_articles.extend(articles.get('articles', []))

    sentiments = analyze_sentiments(all_articles)
    sentiment_file = os.path.join(RAW_DATA_DIR, "aggregated_sentiments.csv")
    save_aggregated_sentiments(sentiments, sentiment_file)
    print(f"Aggregated sentiment data saved to {sentiment_file}")
