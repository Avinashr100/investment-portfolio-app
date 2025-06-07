# Investment in Securities Oversight Board

A Streamlit app to visualize stock portfolios from a single Google Sheet tab "Portfolio".

## Setup

- Make sure the Google Sheet is public.
- The Sheet must have columns: Stock, Broker, Type, Quantity, Investment, Gain
- "Type" should be either "Indian" or "US"
- "Gain" should be in % format (e.g. 10.0)

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
