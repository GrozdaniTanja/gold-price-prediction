import pytest
import requests
from datetime import datetime, timedelta

API_KEY_GOLD = "goldapi-fd3p6tslwqv3gdr-io"
SYMBOL = "XAU"
CURRENCY = "EUR"

API_KEY_NEWS = "ee1cc13b03fc4897bf335dd559a39a6d"
NEWS_URL = "https://newsapi.org/v2/everything"


def test_gold_api_reachability():
    url = f"https://www.goldapi.io/api/{SYMBOL}/{CURRENCY}"
    headers = {
        "x-access-token": API_KEY_GOLD,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200, "Gold API is not reachable"


def test_news_api_reachability():
    today = datetime.today().date()
    from_date = (today - timedelta(days=30)).isoformat()
    to_date = today.isoformat()

    params = {
        'q': 'gold',
        'from': from_date,
        'to': to_date,
        'language': 'en',
        'apiKey': API_KEY_NEWS
    }
    response = requests.get(NEWS_URL, params=params)
    assert response.status_code == 200, "News API is not reachable"


if __name__ == "__main__":
    pytest.main()
