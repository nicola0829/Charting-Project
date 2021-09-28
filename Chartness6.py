import pandas as pd
import yfinance as yf
import plotly as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
from datetime import timedelta
import streamlit as st
import pandas_ta as ta

#Set page to wide mode
st.set_page_config(layout="wide")

#Show all roes and columns when data is printed
pd.set_option('display.max_rows',100000)
pd.set_option('display.max_columns',3000)

# Sidebar
st.sidebar.subheader('Charting')
chart_type = st.sidebar.selectbox("Chart Type", ("Short Term", "Medium Term", "Long Term"))

ticker = st.sidebar.text_input("Ticker", "GOOG") # Select ticker symbol
tickerData = yf.Ticker(ticker)

end_date = st.sidebar.date_input("End date", dt.datetime.now())

if chart_type == "Short Term":
    start_date = st.sidebar.date_input("Start date", dt.datetime.now()-timedelta(days=365))
elif chart_type == "Medium Term":
    start_date = st.sidebar.date_input("Start date", dt.datetime.now()-timedelta(days=1095))
elif chart_type == "Long Term":
    start_date = st.sidebar.date_input("Start date", dt.datetime.now()-timedelta(days=3650))

if chart_type == "Short Term":
    period = "1d"
elif chart_type == "Medium Term":
    period = "1wk"
elif chart_type == "Long Term":
    period = "1mo"

# Ticker information
string_name = tickerData.info['longName']
start = start_date
start_long = start-timedelta(days=3650)
end = end_date

string_logo = '<img src=%s>' % tickerData.info['logo_url']
st.markdown(string_logo, unsafe_allow_html=True)

string_name = tickerData.info['longName']
st.header('**%s**' % string_name)

string_summary = tickerData.info['longBusinessSummary']
st.info(string_summary)

#Get historical data
data = tickerData.history(interval=period, start=start, end=end, auto_adjust=True).reset_index()
data.dropna(inplace=True)
data_LMA = tickerData.history(interval=period, start=start_long, end=end, auto_adjust=True)
data_LMA.dropna(inplace=True)
Adj_Close = data['Close']
Adj_Close_Long = data_LMA['Close']
df_dates = data.loc[:,'Date']

#Get moving average
if chart_type == "Short Term":
    short_MA = abs(Adj_Close_Long.rolling(window=40).mean())
    long_MA = abs(Adj_Close_Long.rolling(window=200).mean())
elif chart_type == "Medium Term":
    short_MA = abs(Adj_Close_Long.rolling(window=22).mean())
    long_MA = abs(Adj_Close_Long.rolling(window=56).mean())
elif chart_type == "Long Term":
    short_MA = abs(Adj_Close_Long.rolling(window=10).mean())
    long_MA = abs(Adj_Close_Long.rolling(window=20).mean())

short_window = short_MA.isna().sum()+1
short_MA2 = short_MA.loc[start:]

long_window = long_MA.isna().sum()+1
long_MA2 = long_MA.loc[start:]

#Calculate RSI
days = 14

delta = Adj_Close_Long.diff()
up = delta.clip(lower=0)
down = -1*delta.clip(upper=0)
ema_up = up.ewm(com=13, adjust=False).mean()
ema_down = down.ewm(com=13, adjust=False).mean()
rs = ema_up/ema_down

RSI = 100 - (100/(1 + rs))
RSI = RSI.loc[start:]

#Calculate MACD
exp1 = Adj_Close_Long.ewm(span=12, adjust=False).mean()
exp11 = exp1.loc[start:]
exp2 = Adj_Close_Long.ewm(span=26, adjust=False).mean()
exp22 = exp2.loc[start:]

MACD = exp11 - exp22
signal = MACD.ewm(span=9, adjust=False).mean()
MACD_diff = MACD - signal

#Calculate Stochastics

data_LMA.ta.stoch(high='High', low='Low', k=14, d=3, append=True)

fast_sto=data_LMA['STOCHk_14_3_3']
fast_sto= fast_sto.loc[start:]

slow_sto=data_LMA['STOCHd_14_3_3']
slow_sto= slow_sto.loc[start:]

#Charting
if chart_type == "Short Term":
    st.header('**Short Term Chart**')
    fig = make_subplots(rows=2, cols=1, row_width=[0.25, 0.75])
    fig.append_trace(go.Candlestick(name="{}".format(ticker), x=df_dates, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="RSI ({})".format(days), x=df_dates, y=RSI), row=2, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=1000)
    fig.update_xaxes(rangeslider_visible=False,
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Medium Term":
    interval = "Weekly"
    st.header('**Medium Term Chart**')
    fig = make_subplots(rows=2, cols=1, row_width=[0.25, 0.75])
    fig.append_trace(go.Candlestick(name="{}".format(ticker), x=df_dates, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MACD (12,26)", x=df_dates, y=MACD), row=2, col=1)
    fig.append_trace(go.Scatter(name="Signal (9)", x=df_dates, y=signal), row=2, col=1)
    fig.append_trace(go.Bar(name="Divergence", x=df_dates, y=MACD_diff), row=2, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=1000)
    #fig.update_yaxes(type='log', row=1, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
elif chart_type == "Long Term":
    st.header('**Long Term Chart**')
    fig = make_subplots(rows=4, cols=1, row_width=[0.15, 0.15, 0.15, 0.55])
    fig.append_trace(go.Candlestick(name="{}".format(ticker), x=df_dates, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']), row=1, col=1,)
    fig.append_trace(go.Scatter(name="MA ({})".format(short_window), x=df_dates, y=short_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MA ({})".format(long_window), x=df_dates, y=long_MA2), row=1, col=1)
    fig.append_trace(go.Scatter(name="MACD (12,26)", x=df_dates, y=MACD), row=2, col=1)
    fig.append_trace(go.Scatter(name="Signal (9)", x=df_dates, y=signal), row=2, col=1)
    fig.append_trace(go.Bar(name="Divergence", x=df_dates, y=MACD_diff), row=2, col=1)
    fig.append_trace(go.Scatter(name="RSI ({})".format(days), x=df_dates, y=RSI), row=3, col=1)
    fig.append_trace(go.Scatter(name="Fast", x=df_dates, y=fast_sto), row=4, col=1)
    fig.append_trace(go.Scatter(name="Slow", x=df_dates, y=slow_sto), row=4, col=1)
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.update_layout(height=1200)
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


#fig.update_xaxes(nticks=100)