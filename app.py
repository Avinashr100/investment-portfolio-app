import streamlit as st
import pandas as pd
import plotly.express as px
from data.google_sheets_connector import load_data

st.set_page_config(page_title="Investment in Securities Oversight Board", layout="wide")
st.markdown("""
<style>
body {
    font-size: 25px;
    color: #111111;
}
</style>
""", unsafe_allow_html=True)

# Inject CSS for table styling
st.markdown(
    "<style>thead tr th { background-color: #003366; color: white; } td:nth-child(2) {{ text-align: center; }}</style>",
    unsafe_allow_html=True
)

st.title("Investment in Securities Oversight Board")




# Load and clean data
df = load_data()
df.columns = df.columns.str.strip()

for col in ['Investment', 'Current Value', 'Quantity']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['Type'] = df['Type'].astype(str).str.strip().str.lower()
df['Type'] = df['Type'].apply(lambda x: 'us' if 'us' in x else 'indian')
df['Broker'] = df['Broker'].astype(str).str.strip()
df['Stock'] = df['Stock'].astype(str).str.strip()

if 'Investment' in df.columns and 'Current Value' in df.columns:
    df['Gain'] = ((df['Current Value'] - df['Investment']) / df['Investment']) * 100

# Split data
indian_df = df[df['Type'] == 'indian'].copy()
us_df = df[df['Type'] == 'us'].copy()

# Dynamic marquee with top gainers and losers
def get_marquee_text(df, label):
    if df.empty or 'Gain' not in df.columns:
        return f"{label}: No data"
    top = df.loc[df['Gain'].idxmax()]
    bottom = df.loc[df['Gain'].idxmin()]
    return f"{label} ↑ {top['Stock']} ({top['Gain']:.1f}%) ↓ {bottom['Stock']} ({bottom['Gain']:.1f}%)"

indian_text = get_marquee_text(indian_df, "🇮🇳 Indian")
us_text = get_marquee_text(us_df, "🇺🇸 US")
marquee_text = f"{indian_text} | {us_text}"

st.markdown(f"<marquee>{marquee_text}</marquee>", unsafe_allow_html=True)


# Formatter
def format_currency(val, currency='INR'):
    if pd.isna(val):
        return "-"
    symbol = '₹' if currency == 'INR' else '$'
    return f"{symbol}{val:,.0f}"

# Summary
total_investment_inr = indian_df['Investment'].sum()
total_gain_inr = indian_df['Current Value'].sum() - total_investment_inr
avg_gain_inr = round((total_gain_inr / total_investment_inr) * 100, 2) if total_investment_inr > 0 else 0

total_investment_usd = us_df['Investment'].sum()
total_gain_usd = us_df['Current Value'].sum() - total_investment_usd
avg_gain_usd = round((total_gain_usd / total_investment_usd) * 100, 2) if total_investment_usd > 0 else 0

# Dual Pie Charts
st.subheader("📊 Investment Distribution by Broker")
col1, col2 = st.columns(2)

with col1:
    if not indian_df.empty:
        pie_data_indian = indian_df.groupby('Broker', as_index=False)['Current Value'].sum()
        fig1 = px.pie(pie_data_indian, names='Broker', values='Current Value', hole=0.3,
                      title="Indian Investments (INR)", width=350, height=350)
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    if not us_df.empty:
        pie_data_us = us_df.groupby('Stock', as_index=False)['Current Value'].sum()
        fig2 = px.pie(pie_data_us, names='Stock', values='Current Value', hole=0.3,
                      title="US Investment Distribution by Stock", width=350, height=350)
        st.plotly_chart(fig2, use_container_width=True)

# Summary Table
st.subheader("📋 Investment Summary (INR vs USD)")
summary_df = pd.DataFrame([
    {
        "Market": "Indian Stocks (INR)",
        "Total Investment": format_currency(total_investment_inr, 'INR'),
        "Current Value": format_currency(indian_df['Current Value'].sum(), 'INR'),
        "Avg Gain/Loss %": f"{avg_gain_inr:.2f}%"
    },
    {
        "Market": "US Stocks (USD)",
        "Total Investment": format_currency(total_investment_usd, 'USD'),
        "Current Value": format_currency(us_df['Current Value'].sum(), 'USD'),
        "Avg Gain/Loss %": f"{avg_gain_usd:.2f}%"
    }
])
st.dataframe(summary_df, use_container_width=True)

# Bar Charts with % Labels
def plot_bar_with_labels(data, title):
    data['GainLabel'] = data['Gain'].map('{:.2f}'.format)
    fig = px.bar(data, x='Stock', y='Gain', color='Broker', title=title, text='GainLabel')
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig

if not indian_df.empty:
    st.subheader("📈 Top Indian Stocks by Gain %")
    fig3 = plot_bar_with_labels(indian_df.sort_values(by='Gain', ascending=False).head(10), "Top Indian Stocks")
    st.plotly_chart(fig3, use_container_width=True)

if not us_df.empty:
    st.subheader("📈 Top US Stocks by Gain %")
    fig4 = plot_bar_with_labels(us_df.sort_values(by='Gain', ascending=False).head(10), "Top US Stocks")
    st.plotly_chart(fig4, use_container_width=True)

# Expandable Holdings by Broker
def display_holdings(df, currency_label):
    for broker in df['Broker'].unique():
        with st.expander(f"{broker} Holdings"):
            broker_df = df[df['Broker'] == broker]
            display_df = broker_df[['Stock', 'Quantity', 'Investment', 'Current Value', 'Gain']].copy()
            display_df['Investment'] = display_df['Investment'].apply(lambda x: format_currency(x, currency_label))
            display_df['Current Value'] = display_df['Current Value'].apply(lambda x: format_currency(x, currency_label))
            display_df['Gain'] = display_df['Gain'].map('{:.2f}%'.format)
            st.dataframe(display_df, use_container_width=True)

if not indian_df.empty:
    st.subheader("📑 All Indian Holdings")
    display_holdings(indian_df, 'INR')

if not us_df.empty:
    st.subheader("📑 All US Holdings")
    display_holdings(us_df, 'USD')
