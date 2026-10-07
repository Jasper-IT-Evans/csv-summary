import pandas as pd
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

grouped = (
    df.groupby(group_col)[value_col]
    .sum()
    .sort_values(ascending=False)
    .rename(f"Total {value_col}")
)

st.dataframe(grouped)
st.bar_chart(grouped)
