# app.py
import numpy as np
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
# Show Live Market Indexes
# Market Ticker Section (Dow, Nasdaq, etc.)
st.subheader("📍 Market Overview")

indexes = {
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq",
    "^GSPC": "S&P 500"
}

for ticker, name in indexes.items():
    index_data = yf.Ticker(ticker).history(period="1d")
    if not index_data.empty:
        price = index_data["Close"].iloc[-1]
        change = index_data["Close"].iloc[-1] - index_data["Open"].iloc[-1]
        pct = (change / index_data["Open"].iloc[-1]) * 100
        color = "🟢" if change > 0 else "🔴"
        st.write(f"{color} **{name}**: ${price:.2f} ({change:+.2f}, {pct:+.2f}%)")

st.title("📈 Stock Tracker and Technical Analysis")

# Input for stock symbol
symbol = st.text_input("Enter stock symbol (e.g. AAPL, TSLA)", "AAPL")

if symbol:
    stock = yf.Ticker(symbol)
    data = stock.history(period="6mo")

    if not data.empty:
        st.write(f"### {symbol} - Last Price: ${data['Close'].iloc[-1]:.2f}")

        # Candlestick + Moving Average
        ma_period = st.slider(
            "Select Moving Average Period (days)", 5, 100, 20)
        data["SMA"] = data["Close"].rolling(window=ma_period).mean()

        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick"
            ),
            go.Scatter(
                x=data.index,
                y=data["SMA"],
                line=dict(color='blue', width=2),
                name=f"{ma_period}-Day SMA"
            )
        ])
        st.plotly_chart(fig)

        # RSI
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        st.subheader("📉 Relative Strength Index (RSI)")
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=data.index, y=data["RSI"], line=dict(color="orange"), name="RSI (14)"))
        rsi_fig.add_hline(y=70, line_dash="dot", line_color="red")
        rsi_fig.add_hline(y=30, line_dash="dot", line_color="green")
        st.plotly_chart(rsi_fig)

        # MACD
        exp1 = data["Close"].ewm(span=12, adjust=False).mean()
        exp2 = data["Close"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        data["MACD"] = macd
        data["Signal"] = signal

        st.subheader("📊 MACD")
        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(
            x=data.index, y=data["MACD"], line=dict(color="blue"), name="MACD"))
        macd_fig.add_trace(go.Scatter(
            x=data.index, y=data["Signal"], line=dict(color="red"), name="Signal Line"))
        st.plotly_chart(macd_fig)
