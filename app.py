import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

# 標題
st.title("股票程式交易系統")

# 連接資料庫
conn = sqlite3.connect("small_stock.db")

# 股票輸入
stock_id = st.text_input("請輸入股票代號", "2330")

# 資料表名稱
table_name = f"stock_kBar_{stock_id}"

try:

    # 讀取資料
    df = pd.read_sql(f"""
    SELECT *
    FROM {table_name}
    """, conn)

    st.write(df.head())

    # 畫收盤價
    st.subheader("收盤價走勢")

    fig1, ax1 = plt.subplots(figsize=(12,6))

    ax1.plot(df['close'])

    st.pyplot(fig1)

    # ===== MACD =====

    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()

    df['DIF'] = df['EMA12'] - df['EMA26']

    df['MACD'] = df['DIF'].ewm(span=9).mean()

    # MACD訊號
    df['Signal'] = 0

    df.loc[df['DIF'] > df['MACD'], 'Signal'] = 1
    df.loc[df['DIF'] < df['MACD'], 'Signal'] = -1

    # 報酬率
    df['Return'] = df['close'].pct_change()

    # 策略報酬
    df['MACD_Strategy_Return'] = df['Signal'].shift(1) * df['Return']

    # 累積報酬
    df['MACD_Cumulative_Return'] = (1 + df['MACD_Strategy_Return']).cumprod()

    # MACD圖
    st.subheader("MACD")

    fig2, ax2 = plt.subplots(figsize=(12,6))

    ax2.plot(df['DIF'], label='DIF')
    ax2.plot(df['MACD'], label='MACD')

    ax2.legend()

    st.pyplot(fig2)

    # MACD績效
    st.subheader("MACD策略績效")

    fig3, ax3 = plt.subplots(figsize=(12,6))

    ax3.plot(df['MACD_Cumulative_Return'])

    st.pyplot(fig3)

    # 總報酬
    total_return = df['MACD_Cumulative_Return'].iloc[-1] - 1

    st.write("MACD總報酬率：", round(total_return * 100,2), "%")

    # ===== KDJ =====

    low_list = df['low'].rolling(9).min()
    high_list = df['high'].rolling(9).max()

    df['RSV'] = (df['close'] - low_list) / (high_list - low_list) * 100

    df['K'] = df['RSV'].ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    # KDJ訊號
    df['KDJ_Signal'] = 0

    df.loc[df['K'] > df['D'], 'KDJ_Signal'] = 1
    df.loc[df['K'] < df['D'], 'KDJ_Signal'] = -1

    # KDJ報酬
    df['KDJ_Strategy_Return'] = df['KDJ_Signal'].shift(1) * df['Return']

    # KDJ累積報酬
    df['KDJ_Cumulative_Return'] = (1 + df['KDJ_Strategy_Return']).cumprod()

    # KDJ圖
    st.subheader("KDJ")

    fig4, ax4 = plt.subplots(figsize=(12,6))

    ax4.plot(df['K'], label='K')
    ax4.plot(df['D'], label='D')
    ax4.plot(df['J'], label='J')

    ax4.legend()

    st.pyplot(fig4)

    # KDJ績效
    st.subheader("KDJ策略績效")

    fig5, ax5 = plt.subplots(figsize=(12,6))

    ax5.plot(df['KDJ_Cumulative_Return'])

    st.pyplot(fig5)

    # KDJ總報酬
    kdj_return = df['KDJ_Cumulative_Return'].iloc[-1] - 1

    st.write("KDJ總報酬率：", round(kdj_return * 100,2), "%")

except:

    st.error("找不到股票資料")