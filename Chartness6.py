import pandas as pd
import yfinance as yf
import plotly as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
from datetime import timedelta
import streamlit as st

#Set page to wide mode
st.set_page_config(layout="wide")

# Sidebar
st.sidebar.subheader('Charting')
chart_type = st.sidebar.selectbox("Chart Type", ("Short Term", "Medium Term", "Long Term"))

ticker = st.sidebar.text_input("Ticker", "GOOG") # Select ticker symbol
tickerData = yf.Ticker(ticker)


start_date = st.sidebar.date_input("Start date", dt.date(2019, 1, 1))
end_date = st.sidebar.date_input("End date", dt.date(2021, 1, 31))

interval = st.sidebar.selectbox("Period", ("Daily", "Weekly", "Monthly"))

string_name = tickerData.info['longName']
start = start_date
start_long = start-timedelta(days=3000)
end = end_date

# Ticker information
string_logo = '<img src=%s>' % tickerData.info['logo_url']
st.markdown(string_logo, unsafe_allow_html=True)

string_name = tickerData.info['longName']
st.header('**%s**' % string_name)

string_summary = tickerData.info['longBusinessSummary']
st.info(string_summary)

data = tickerData.history(interval='1d', start=start, end=end, auto_adjust=True).reset_index()
data_clean = data.fillna(method='ffill')
data_LMA = tickerData.history(interval='1d', start=start_long, end=end, auto_adjust=True)
data_LMA_clean = data_LMA.fillna(method='ffill')
df_dates = data.loc[:,'Date']

delta = data_clean['Close'].diff(1)
Adj_Close = data_clean['Close']
Adj_Close_Long = data_LMA_clean['Close']
delta.dropna(inplace=True)

positive = delta.copy()
negative = delta.copy()

positive[positive < 0] = 0
negative[negative > 0] = 0

days = 14

short_MA = abs(Adj_Close_Long.rolling(window=40).mean())
short_window = short_MA.isna().sum()+1
short_MA2 = short_MA.loc[start:]

long_MA = abs(Adj_Close_Long.rolling(window=200).mean())
long_window = long_MA.isna().sum()+1
long_MA2 = long_MA.loc[start:]

average_gain = positive.ewm(com=13, adjust=False).mean()
average_loss = negative.abs().ewm(com=13, adjust=False).mean()

relative_strength = average_gain / average_loss
RSI = 100.0 - (100.0 / (1.0 + relative_strength))

RSI = RSI.iloc[14:]

if chart_type == "Short Term":
    st.header('**Short Term Chart**')
    fig = make_subplots(rows=2, cols=1, row_width=[0.25, 0.75])
    fig.append_trace(go.Scatter(name="{}".format(ticker), x=df_dates, y=Adj_Close), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="RSI ({})".format(days), x=df_dates, y=RSI), row=2, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Medium Term":
    st.header('**Medium Term Chart**')
    fig = make_subplots(rows=2, cols=1, row_width=[0.25, 0.75])
    fig.append_trace(go.Scatter(name="{}".format(ticker), x=df_dates, y=Adj_Close), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="RSI ({})".format(days), x=df_dates, y=RSI), row=2, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Long Term":
    st.header('**Long Term Chart**')
    fig = make_subplots(rows=2, cols=1, row_width=[0.25, 0.75])
    fig.append_trace(go.Scatter(name="{}".format(ticker), x=df_dates, y=Adj_Close), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="RSI ({})".format(days), x=df_dates, y=RSI), row=2, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)


#fig.update_xaxes(nticks=100)