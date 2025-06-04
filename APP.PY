# app.py
import numpy as np
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

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
# Show Live Market Indexes
st.markdown("### 📊 Market Overview")

indexes = {
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC"
}

cols = st.columns(len(indexes))

for i, (name, ticker) in enumerate(indexes.items()):
    index_data = yf.Ticker(ticker).history(period="1d", interval="1m")
    if not index_data.empty:
        last_price = index_data["Close"].iloc[-1]
        prev_close = index_data["Close"].iloc[0]
        change = last_price - prev_close
        pct = (change / prev_close) * 100
        color = "green" if change > 0 else "red"

        cols[i].markdown(f"""
        <div style='text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9'>
            <b>{name}</b><br>
            <span style='font-size: 20px; color: {color}'>${last_price:,.2f}</span><br>
            <span style='color: {color}'>{change:+.2f} ({pct:+.2f}%)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols[i].write(f"{name}: data not available")
