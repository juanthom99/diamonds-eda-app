import os

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(page_title="Diamonds Dashboard", layout="wide")


@st.cache_data(ttl=600)
def load_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)

    all_rows = []
    page_size = 1000
    start = 0
    while True:
        resp = (
            supabase.table("diamonds")
            .select("*")
            .range(start, start + page_size - 1)
            .execute()
        )
        rows = resp.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        start += page_size

    return pd.DataFrame(all_rows)


df = load_data()

st.title("Diamonds Dashboard")
st.caption(f"Data loaded from Supabase — {len(df):,} rows")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Distributions", "Price Relationships", "Correlation Heatmap"]
)

with tab1:
    st.subheader("Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Diamonds", f"{len(df):,}")
    col2.metric("Average Price", f"${df['price'].mean():,.0f}")
    col3.metric("Average Carat", f"{df['carat'].mean():.2f}")
    st.dataframe(df.head(20))

with tab2:
    st.subheader("Distributions")
    numeric_col = st.selectbox(
        "Choose a numeric column", ["carat", "price", "depth", "table"]
    )
    fig, ax = plt.subplots()
    sns.histplot(df[numeric_col], kde=True, ax=ax)
    ax.set_title(f"Distribution of {numeric_col}")
    st.pyplot(fig)

    cat_col = st.selectbox("Choose a categorical column", ["cut", "color", "clarity"])
    fig2, ax2 = plt.subplots()
    df[cat_col].value_counts().plot(kind="bar", ax=ax2)
    ax2.set_title(f"Count by {cat_col}")
    st.pyplot(fig2)

with tab3:
    st.subheader("Price Relationships")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=df.sample(min(3000, len(df))), x="carat", y="price", alpha=0.4, ax=ax3)
    ax3.set_title("Carat vs Price")
    st.pyplot(fig3)

    group_col = st.selectbox("Group price by", ["cut", "color", "clarity"])
    fig4, ax4 = plt.subplots()
    sns.boxplot(data=df, x=group_col, y="price", ax=ax4)
    ax4.set_title(f"Price Distribution by {group_col}")
    st.pyplot(fig4)

with tab4:
    st.subheader("Correlation Heatmap")
    numeric_df = df.select_dtypes(include="number")
    fig5, ax5 = plt.subplots(figsize=(8, 6))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax5)
    st.pyplot(fig5)