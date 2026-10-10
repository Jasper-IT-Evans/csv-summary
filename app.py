import pandas as pd
import requests
import streamlit as st

st.title("CSV summary")

uploaded = st.file_uploader("Upload a CSV", type="csv")

if uploaded is None:
    st.info("Upload a CSV to get started. Try sample_data.csv.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception:
    st.error(
        "Sorry, we couldn't read that file as a CSV. "
        "Check it's a comma-separated text file with a header row, then try again."
    )
    st.stop()

if df.empty:
    st.error("That file has no data rows. Check it and try again.")
    st.stop()

st.subheader("First 10 rows")
st.dataframe(df.head(10))

numeric_cols = df.select_dtypes(include="number").columns.tolist()
text_cols = df.select_dtypes(exclude="number").columns.tolist()

st.subheader("Summary statistics")
if numeric_cols:
    st.dataframe(df[numeric_cols].describe())
else:
    st.warning("No numeric columns found.")

st.subheader("Totals by group")
if not numeric_cols or not text_cols:
    st.warning("Grouping needs at least one text column and one numeric column.")
    st.stop()

group_col = st.selectbox("Group by (text column)", text_cols)
value_col = st.selectbox("Total of (numeric column)", numeric_cols)



@st.cache_data(ttl=3600)
def get_rates():
    key = st.secrets["EXCHANGE_RATE_API_KEY"]
    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/{key}/latest/GBP", timeout=10
    )
    response.raise_for_status()
    data = response.json()
    if data.get("result") != "success":
        raise ValueError("Exchange rate request was not successful")
    return data["conversion_rates"]


try:
    rates = get_rates()
    currencies = ["GBP", "EUR", "USD"]
except (KeyError, FileNotFoundError, ValueError, requests.RequestException):
    st.warning("Couldn't get live exchange rates, so amounts are shown in GBP.")
    rates = {"GBP": 1.0}
    currencies = ["GBP"]

currency = st.selectbox("Currency", currencies)

grouped = (
    (df.groupby(group_col)[value_col].sum() * rates[currency])
    .sort_values(ascending=False)
    .rename(f"Total {value_col} ({currency})")
)

st.dataframe(grouped)
st.bar_chart(grouped)
