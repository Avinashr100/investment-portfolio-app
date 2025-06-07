import streamlit as st
import pandas as pd
import plotly.express as px
from data.google_sheets_connector import load_data

st.set_page_config(page_title="Investment in Securities Oversight Board", layout="wide")

st.title("Investment in Securities Oversight Board")
st.markdown("<marquee>📈 Live Portfolio View | Track Your Indian and US Stock Investments</marquee>", unsafe_allow_html=True)

# Load data
df = load_data()

# Clean and prepare data
df.columns = df.columns.str.strip()
df['Investment'] = pd.to_numeric(df['Investment'], errors='coerce')
df['Gain'] = df['Gain'].astype(str).str.replace('%', '', regex=False).astype(float)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Type'] = df['Type'].str.strip().str.lower()
df['Broker'] = df['Broker'].str.strip()

# Separate Indian and US stocks
indian_df = df[df['Type'] == 'indian']
us_df = df[df['Type'] == 'us']

# Combined Indian investments summary
total_investment_inr = indian_df['Investment'].sum()
total_gain_inr = (indian_df['Investment'] * indian_df['Gain'] / 100).sum()
avg_gain_inr = round((total_gain_inr / total_investment_inr) * 100, 2)

# Pie chart by Broker (Indian only)
st.subheader("📊 Investment Distribution by Broker (INR only)")
broker_inr = indian_df.groupby('Broker', as_index=False)['Investment'].sum()
fig_broker = px.pie(broker_inr, names='Broker', values='Investment',
                    title="Indian Investment by Broker", hole=0.3)
st.plotly_chart(fig_broker, use_container_width=True)

# Combined Summary Table
st.subheader("📋 Investment Summary (INR vs USD)")

summary_df = pd.DataFrame([
    {
        "Market": "Indian Stocks (INR)",
        "Total Investment": total_investment_inr,
        "Avg Gain/Loss %": avg_gain_inr
    },
    {
        "Market": "US Stocks (USD)",
        "Total Investment": us_df['Investment'].sum(),
        "Avg Gain/Loss %": round((us_df['Investment'] * us_df['Gain'] / 100).sum() / us_df['Investment'].sum() * 100, 2)
    }
])
st.dataframe(summary_df, use_container_width=True)

# Bar chart of gain by stock
st.subheader("📈 Top Indian Stocks by Gain %")
top_indian = indian_df.sort_values(by='Gain', ascending=False).head(10)
fig_gain = px.bar(top_indian, x='Stock', y='Gain', color='Broker', title="Top 10 Indian Stocks by Gain %")
st.plotly_chart(fig_gain, use_container_width=True)

st.subheader("📈 Top US Stocks by Gain %")
top_us = us_df.sort_values(by='Gain', ascending=False).head(10)
fig_us = px.bar(top_us, x='Stock', y='Gain', color='Broker', title="Top 10 US Stocks by Gain %")
st.plotly_chart(fig_us, use_container_width=True)

# Table view
st.subheader("📑 All Indian Holdings")
st.dataframe(indian_df[['Stock', 'Broker', 'Quantity', 'Investment', 'Gain']], use_container_width=True)

st.subheader("📑 All US Holdings")
st.dataframe(us_df[['Stock', 'Broker', 'Quantity', 'Investment', 'Gain']], use_container_width=True)
