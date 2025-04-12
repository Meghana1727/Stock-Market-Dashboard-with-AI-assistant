import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import datetime
import streamlit as st

# Finnhub API Key (Replace with your API Key)
FINNHUB_API_KEY = "cv74ra9r01qsq464svq0cv74ra9r01qsq464svqg"

def get_sp500_tickers():
    """Fetches S&P 500 tickers and their sectors from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(str(table))[0]
    return df[['Symbol', 'GICS Sector']]

def get_latest_earnings_release():
    """Fetches latest earnings release dates from Finnhub API."""
    url = f"https://finnhub.io/api/v1/calendar/earnings?token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    today = datetime.date.today()
    latest_earnings = [
        {"symbol": item["symbol"], "release_date": item["date"]}
        for item in data.get("earningsCalendar", []) 
        if "date" in item and datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() > today - datetime.timedelta(days=90)
    ]
    
    return latest_earnings

def fetch_eps_growth(ticker):
    """Fetches EPS growth from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        income_statement = stock.income_stmt
        if income_statement is None or income_statement.empty:
            return None, None
        
        quarters = income_statement.columns[:2]
        if len(quarters) < 2:
            return None, None
        
        latest_eps = income_statement.at["Diluted EPS", quarters[0]] if "Diluted EPS" in income_statement.index else 0
        prev_eps = income_statement.at["Diluted EPS", quarters[1]] if "Diluted EPS" in income_statement.index else 0
        eps_growth = ((latest_eps - prev_eps) / (prev_eps if prev_eps != 0 else 1)) * 100
        
        return latest_eps, eps_growth
    except:
        return None, None

def plot_candlestick(ticker, release_date):
    """Generates a candlestick chart for a given stock and earnings release date."""
    try:
        stock = yf.Ticker(ticker)
        release_date = datetime.datetime.strptime(release_date, "%Y-%m-%d")
        start_date = (release_date - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (release_date + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            return None
        
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker
        )])
        
        fig.update_layout(title=f"Candlestick Chart for {ticker} (Earnings Release: {release_date.strftime('%Y-%m-%d')})",
                          xaxis_title="Date",
                          yaxis_title="Stock Price",
                          xaxis_rangeslider_visible=False)
        return fig
    except Exception as e:
        return None

def get_stock_news(ticker):
    """Fetches the latest 8 months of stock news from Finnhub API."""
    try:
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=240)).strftime('%Y-%m-%d')  # 8 months ago
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start_date}&to={today}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        news_articles = []
        for item in data:
            news_articles.append({
                "headline": item.get("headline", "No title"),
                "url": item.get("url", "#"),
                "datetime": datetime.datetime.utcfromtimestamp(item["datetime"]).strftime('%Y-%m-%d') if "datetime" in item else "Unknown date",
                "summary": item.get("summary", "No summary available.")
            })
        
        return news_articles[:5]  # Limit to 5 latest articles
    except Exception as e:
        return []

def quarterly_analysis(selected_ticker):
    """Analyzes quarterly earnings, EPS growth, candlestick charts, and fetches news."""
    latest_stocks = get_latest_earnings_release()
    stock_info = next((stock for stock in latest_stocks if stock["symbol"] == selected_ticker), None)

    if stock_info:
        release_date = stock_info["release_date"]
        latest_eps, eps_growth = fetch_eps_growth(selected_ticker)
        
        # Create DataFrame for Earnings Report
        earnings_data = {
            "Stock Symbol": [selected_ticker],
            "Release Date": [release_date],
            "Latest EPS": [latest_eps],
            "EPS Growth (%)": [eps_growth]
        }
        earnings_df = pd.DataFrame(earnings_data)
        
        # Generate Candlestick Chart
        candlestick_chart = plot_candlestick(selected_ticker, release_date)
        
        return earnings_df, candlestick_chart
    else:
        return pd.DataFrame(), None  # Empty DataFrame if no data found
