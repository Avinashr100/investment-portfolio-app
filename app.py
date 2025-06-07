import streamlit as st
import pandas as pd
import plotly.express as px
from data.google_sheets_connector import load_data

st.set_page_config(page_title="Investment in Securities Oversight Board", layout="wide")

st.title("Investment in Securities Oversight Board")
st.markdown("<marquee>📈 Live Portfolio View | Track Your Indian and US Stock Investments</marquee>", unsafe_allow_html=True)

# Load data
df = load_data()

# Data cleaning
df.columns = df.columns.str.strip()
for col in ['Investment', 'Current Value', 'Quantity']:
    df[col] = df[col].astype(str).str.replace(',', '', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['Type'] = df['Type'].str.strip().str.lower()
df['Broker'] = df['Broker'].str.strip()
df['Stock'] = df['Stock'].str.strip()

# Compute actual gain %: (Current Value - Investment) / Investment * 100
df['Gain'] = ((df['Current Value'] - df['Investment']) / df['Investment']) * 100

# Split by type
indian_df = df[df['Type'] == 'indian'].copy()
us_df = df[df['Type'] == 'us'].copy()

# Summary calculations
total_investment_inr = indian_df['Investment'].sum()
total_gain_inr = indian_df['Current Value'].sum() - total_investment_inr
avg_gain_inr = round((total_gain_inr / total_investment_inr) * 100, 2)

total_investment_usd = us_df['Investment'].sum()
total_gain_usd = us_df['Current Value'].sum() - total_investment_usd
avg_gain_usd = round((total_gain_usd / total_investment_usd) * 100, 2)

# PIE CHART - Indian investments by Broker
st.subheader("📊 Investment Distribution by Broker (INR only)")
if not indian_df.empty:
    broker_inr = indian_df.groupby('Broker', as_index=False)['Investment'].sum()
    fig_broker = px.pie(broker_inr, names='Broker', values='Investment',
                        title="Indian Investment by Broker", hole=0.3)
    st.plotly_chart(fig_broker, use_container_width=True)
else:
    st.info("No Indian stock data available.")

# Investment summary
st.subheader("📋 Investment Summary (INR vs USD)")
summary_df = pd.DataFrame([
    {
        "Market": "Indian Stocks (INR)",
        "Total Investment": total_investment_inr,
        "Avg Gain/Loss %": avg_gain_inr
    },
    {
        "Market": "US Stocks (USD)",
        "Total Investment": total_investment_usd,
        "Avg Gain/Loss %": avg_gain_usd
    }
])
st.dataframe(summary_df, use_container_width=True)

# Bar Charts
if not indian_df.empty:
    st.subheader("📈 Top Indian Stocks by Gain %")
    top_indian = indian_df.sort_values(by='Gain', ascending=False).head(10)
    fig_gain = px.bar(top_indian, x='Stock', y='Gain', color='Broker', title="Top 10 Indian Stocks by Gain %")
    st.plotly_chart(fig_gain, use_container_width=True)

if not us_df.empty:
    st.subheader("📈 Top US Stocks by Gain %")
    top_us = us_df.sort_values(by='Gain', ascending=False).head(10)
    fig_us = px.bar(top_us, x='Stock', y='Gain', color='Broker', title="Top 10 US Stocks by Gain %")
    st.plotly_chart(fig_us, use_container_width=True)

# Tables
if not indian_df.empty:
    st.subheader("📑 All Indian Holdings")
    st.dataframe(indian_df[['Stock', 'Broker', 'Quantity', 'Investment', 'Current Value', 'Gain']], use_container_width=True)

if not us_df.empty:
    st.subheader("📑 All US Holdings")
    st.dataframe(us_df[['Stock', 'Broker', 'Quantity', 'Investment', 'Current Value', 'Gain']], use_container_width=True)
