import yfinance as yf
import json
import os
from datetime import datetime, timedelta, timezone
import pytz
from sentiment_analyser import SentimentAnalyzer

script_dir = os.path.dirname(os.path.abspath(__file__))

def _load_and_filter_existing_news(output_file, cutoff_date_utc):
    """Loads existing news from a file and filters it based on cutoff date (UTC)."""
    existing_news = []
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            try:
                data = json.load(f)
                existing_news = data.get("news", [])
            except json.JSONDecodeError:
                print(f"Warning: Existing {output_file} is corrupted. Overwriting.")

    filtered_existing_news = []
    for item in existing_news:
        if isinstance(item, dict) and 'date' in item:
            try:
                item_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                if item_date >= cutoff_date_utc:
                    filtered_existing_news.append(item)
            except ValueError:
                print(f"Warning: Invalid date format in item: {item}")
        elif isinstance(item, dict):
            filtered_existing_news.append(item)
    return filtered_existing_news

def _fetch_and_process_new_news(ticker_symbol, analyzer, cutoff_date_utc, existing_ids):
    """Fetches new news, processes it, and calculates sentiment."""
    new_news = []
    new_count = 0
    stock = yf.Ticker(ticker_symbol)
    news = stock.news
    if news:
        for article in news:
            id = article['id']
            pub_date_str = article['content']['pubDate']
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            if pub_date >= cutoff_date_utc and id not in existing_ids:
                summary = article['content']['summary']
                sentiment_score = analyzer.analyze_sentiment(summary)
                new_news.append({"id": id, "summary": summary, "date": pub_date_str, "sentiment-score": sentiment_score})
                new_count += 1
    return new_news, new_count

def get_stock_news_json(ticker_symbol, analyzer, cutoff_date_utc):
    """
    Retrieves news summaries for a stock, filters existing news, and saves them to a structured JSON file.
    """
    try:
        output_file = os.path.join(script_dir,"..", "data","news_data", f"{ticker_symbol.lower()}_news.json")
        filtered_existing_news = _load_and_filter_existing_news(output_file, cutoff_date_utc)
        existing_ids = {item['id'] for item in filtered_existing_news if isinstance(item, dict) and 'id' in item}
        new_news, new_count = _fetch_and_process_new_news(ticker_symbol, analyzer, cutoff_date_utc, existing_ids)
        all_news = filtered_existing_news + new_news
        sentiment_scores = [item["sentiment-score"] for item in all_news if isinstance(item, dict) and "sentiment-score" in item]
        average_sentiment = sum(sentiment_scores) / len(sentiment_scores) if all_news and sentiment_scores else 0
        weighted_average = _calculate_weighted_average(all_news)
        average_daily_sentiments = _calculate_average_daily_sentiments(all_news)
        data_to_save = {
            "ticker": ticker_symbol,
            "total_news": len(all_news),
            "average_sentiment": average_sentiment,
            "weighted_average_sentiment": weighted_average,
            "average_daily_sentiments": average_daily_sentiments,
            "news": all_news,
        }
        with open(output_file, "w") as f:
            json.dump(data_to_save, f, indent=4)
        print(f"{new_count} new news summaries for {ticker_symbol} saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_stock_data(json_data, max_age_days):
    """
    Loops through the stock list, gathers the news for each ticker.
    """
    analyzer = SentimentAnalyzer()
    eastern = pytz.timezone('US/Eastern')
    now_eastern = datetime.now(eastern)
    cutoff_eastern = now_eastern - timedelta(days=max_age_days)
    cutoff_utc = cutoff_eastern.astimezone(timezone.utc)
    for stock in json_data:
        ticker = stock["ticker"]
        get_stock_news_json(ticker, analyzer, cutoff_utc)
    del analyzer

def _calculate_weighted_average(news_list):
    """Calculates the weighted average of sentiment scores, downgrading weight by 15% daily."""
    if not news_list:
        return 0
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    weighted_sum = 0
    total_weight = 0
    for item in news_list:
        if isinstance(item, dict) and 'date' in item and 'sentiment-score' in item:
            try:
                item_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00')).replace(hour=0, minute=0, second=0, microsecond=0)
                days_diff = (today - item_date).days
                if 0 <= days_diff <= 6:
                    weight = 1 - (days_diff * 0.15)
                    weighted_sum += item["sentiment-score"] * weight
                    total_weight += weight
                else:
                    weight = 0 # should not happen, but added for safety
            except ValueError:
                print(f"Warning: Invalid date format in item: {item}")
    return weighted_sum / total_weight if total_weight else 0

def _calculate_average_daily_sentiments(news_list):
    """Calculates the average daily sentiment scores."""
    daily_sentiments = [[] for _ in range(7)]
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    for item in news_list:
        if isinstance(item, dict) and 'date' in item and 'sentiment-score' in item:
            try:
                item_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00')).replace(hour=0, minute=0, second=0, microsecond=0)
                days_diff = (today - item_date).days
                if 0 <= days_diff < 7:
                    daily_sentiments[days_diff].append(item["sentiment-score"])
            except ValueError:
                print(f"Warning: Invalid date format in item: {item}")

    return [sum(day) / len(day) if day else 0 for day in daily_sentiments]

def give_recommendations(stock_data):
    """
    Calculates and saves top 5 best and worst performing stocks based on weighted average sentiment.
    """
    recommendations_file = os.path.join(script_dir, "..", "data", "recommendations.json")
    ticker_sentiments = []

    for stock in stock_data:
        ticker = stock["ticker"]
        output_file = os.path.join(script_dir, "..", "data", "news_data", f"{ticker.lower()}_news.json")
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                try:
                    data = json.load(f)
                    weighted_average = data.get("weighted_average_sentiment", 0)
                    ticker_sentiments.append({"ticker": ticker, "weighted_average": weighted_average})
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"Error reading {output_file}: {e}")

    sorted_tickers = sorted(ticker_sentiments, key=lambda x: x["weighted_average"], reverse=True)

    top_5_best = sorted_tickers[:5]
    top_5_worst = sorted_tickers[-5:]

    recommendations = {
        "top_5_best": top_5_best,
        "top_5_worst": top_5_worst
    }

    with open(recommendations_file, "w") as f:
        json.dump(recommendations, f, indent=4)

    print(f"Recommendations saved to {recommendations_file}")

if __name__ == "__main__":
    max_age_days = 7
    try:
        stocklist_filepath = os.path.join(script_dir, "..", "data", "stocklist.json")
        with open(stocklist_filepath, "r") as f:
            stock_data = json.load(f)
        process_stock_data(stock_data, max_age_days)
        give_recommendations(stock_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")