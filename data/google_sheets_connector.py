import pandas as pd

def load_data():
    sheet_id = "1Qrbv0ofpo8vSQZyPVGIhIiES9DIvsqwdnsSFTEla630"
    gid = "1567229075"  # New tab "Portfolio"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df
