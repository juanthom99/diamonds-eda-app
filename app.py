"""
Diamonds Dataset ΓÇö Exploratory Data Analysis
A Streamlit app that loads the diamonds.csv dataset, cleans it, and walks
through a full EDA: structure, distributions, outliers, and relationships
between diamond characteristics and price.
"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

st.set_page_config(page_title="Diamonds EDA", layout="wide")

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

CAT_ORDER = {
    "cut": ["Fair", "Good", "Very Good", "Premium", "Ideal"],
    "color": ["J", "I", "H", "G", "F", "E", "D"],
    "clarity": ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"],
}


@st.cache_data
def load_raw():
    return pd.read_csv("data/diamonds.csv")


@st.cache_data
def clean_data(df: pd.DataFrame):
    """Drop duplicate rows and physically impossible measurements.

    Returns the cleaned frame plus a short log of what was removed, so the
    cleaning step stays visible instead of silently altering the data.
    """
    log = []
    start = len(df)

    df = df.drop_duplicates()
    log.append(f"Dropped {start - len(df)} exact duplicate rows.")

    before = len(df)
    df = df[(df["x"] > 0) & (df["y"] > 0) & (df["z"] > 0)]
    log.append(f"Dropped {before - len(df)} rows with a 0mm x/y/z dimension (data entry errors).")

    # y and z have a couple of extreme outliers (e.g. y=58.9mm) that are almost
    # certainly typos (missing decimal point) rather than real diamonds.
    before = len(df)
    df = df[(df["y"] < 20) & (df["z"] < 20)]
    log.append(f"Dropped {before - len(df)} rows with y or z > 20mm (implausible for a diamond, likely typos).")

    df = df.reset_index(drop=True)

    for col, order in CAT_ORDER.items():
        df[col] = pd.Categorical(df[col], categories=order, ordered=True)

    return df, log


raw = load_raw()
df, cleaning_log = clean_data(raw)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.header("Filters")
carat_range = st.sidebar.slider(
    "Carat range",
    float(df["carat"].min()),
    float(df["carat"].max()),
    (float(df["carat"].min()), float(df["carat"].max())),
)
cut_sel = st.sidebar.multiselect("Cut", CAT_ORDER["cut"], default=CAT_ORDER["cut"])
color_sel = st.sidebar.multiselect("Color", CAT_ORDER["color"], default=CAT_ORDER["color"])

fdf = df[
    (df["carat"].between(*carat_range))
    & (df["cut"].isin(cut_sel))
    & (df["color"].isin(color_sel))
]

st.sidebar.caption(f"{len(fdf):,} of {len(df):,} cleaned rows match the current filters.")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("≡ƒÆÄ Diamonds Dataset ΓÇö Exploratory Data Analysis")
st.markdown(
    "Dataset: [`diamonds.csv`](https://github.com/mwaskom/seaborn-data) ΓÇö "
    "53,940 round-cut diamonds with 4 quality attributes (the 4 Cs), "
    "physical dimensions, and price. Filters in the sidebar apply to every "
    "chart below."
)

tabs = st.tabs([
    "1. Overview & Cleaning",
    "2. Distributions",
    "3. Outliers",
    "4. Relationships with Price",
    "5. Correlation",
])

# ---------------------------------------------------------------------------
# Tab 1 ΓÇö Overview & cleaning
# ---------------------------------------------------------------------------

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw rows", f"{len(raw):,}")
    c2.metric("Cleaned rows", f"{len(df):,}")
    c3.metric("Columns", df.shape[1])
    c4.metric("Missing values", int(df.isna().sum().sum()))

    st.subheader("Cleaning log")
    st.markdown("I removed rows that would distort the analysis rather than reflect real diamonds:")
    for line in cleaning_log:
        st.markdown(f"- {line}")
    st.caption(
        "No columns were dropped ΓÇö every field (carat, cut, color, clarity, depth, "
        "table, price, x, y, z) is independently informative for this analysis."
    )

    st.subheader("Sample of cleaned data")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Data types & summary statistics")
    left, right = st.columns([1, 2])
    with left:
        st.write(df.dtypes.astype(str).rename("dtype"))
    with right:
        st.dataframe(df.describe().T, use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 2 ΓÇö Distributions
# ---------------------------------------------------------------------------

with tabs[1]:
    st.subheader("Numeric distributions")
    num_cols = ["carat", "price", "depth", "table", "x", "y", "z"]
    choice = st.selectbox("Pick a numeric column", num_cols, index=0)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(fdf[choice], kde=True, ax=ax[0], color="#4c72b0")
    ax[0].set_title(f"Distribution of {choice}")
    sns.boxplot(x=fdf[choice], ax=ax[1], color="#dd8452")
    ax[1].set_title(f"Boxplot of {choice}")
    st.pyplot(fig)

    skew = fdf[choice].skew()
    st.caption(
        f"Skewness: {skew:.2f}. "
        + ("Right-skewed ΓÇö a handful of large/expensive stones stretch the tail."
           if skew > 0.5 else
           "Left-skewed." if skew < -0.5 else
           "Roughly symmetric.")
    )

    st.subheader("Categorical breakdown")
    cat_choice = st.selectbox("Pick a categorical column", ["cut", "color", "clarity"], index=0)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    order = CAT_ORDER[cat_choice]
    sns.countplot(data=fdf, x=cat_choice, order=order, hue=cat_choice, palette="viridis", legend=False, ax=ax2)
    ax2.set_title(f"Count of diamonds by {cat_choice}")
    for p in ax2.patches:
        ax2.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2, p.get_height()),
                     ha="center", va="bottom", fontsize=8)
    st.pyplot(fig2)

# ---------------------------------------------------------------------------
# Tab 3 ΓÇö Outliers
# ---------------------------------------------------------------------------

with tabs[2]:
    st.subheader("Outlier detection (IQR method)")
    st.markdown(
        "For each numeric column I flag points beyond 1.5├ùIQR from the quartiles "
        "and report the share of rows affected, on the *cleaned* data (typos already removed)."
    )

    rows = []
    for col in num_cols:
        q1, q3 = fdf[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = ((fdf[col] < low) | (fdf[col] > high)).sum()
        rows.append({"column": col, "lower_bound": round(low, 2), "upper_bound": round(high, 2),
                     "n_outliers": n_out, "pct_outliers": round(100 * n_out / len(fdf), 2)})
    out_df = pd.DataFrame(rows).sort_values("pct_outliers", ascending=False)
    st.dataframe(out_df, use_container_width=True)

    st.subheader("Carat vs. price, with outliers highlighted")
    q1, q3 = fdf["price"].quantile([0.25, 0.75])
    iqr = q3 - q1
    high = q3 + 1.5 * iqr
    is_out = fdf["price"] > high

    fig3, ax3 = plt.subplots(figsize=(9, 5))
    ax3.scatter(fdf.loc[~is_out, "carat"], fdf.loc[~is_out, "price"], s=6, alpha=0.3, label="typical", color="#4c72b0")
    ax3.scatter(fdf.loc[is_out, "carat"], fdf.loc[is_out, "price"], s=8, alpha=0.6, label="price outlier (>1.5├ùIQR)", color="#c44e52")
    ax3.set_xlabel("carat")
    ax3.set_ylabel("price ($)")
    ax3.legend()
    st.pyplot(fig3)
    st.caption(
        "Price outliers aren't data errors ΓÇö they're large, high-clarity stones. "
        "I keep them: they're real and are exactly what drives the top end of the price curve."
    )

# ---------------------------------------------------------------------------
# Tab 4 ΓÇö Relationships with price
# ---------------------------------------------------------------------------

with tabs[3]:
    st.subheader("Carat vs. price")
    fig4, ax4 = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=fdf.sample(min(5000, len(fdf)), random_state=1),
                     x="carat", y="price", hue="clarity", palette="viridis", s=15, alpha=0.6, ax=ax4)
    ax4.set_title("Carat vs. price, colored by clarity (5,000-row sample for readability)")
    st.pyplot(fig4)
    st.caption(
        f"Correlation between carat and price: {fdf['carat'].corr(fdf['price']):.2f}. "
        "The relationship is strongly positive but convex ΓÇö price accelerates as carat grows, "
        "which is why a log transform is standard before modeling this dataset."
    )

    st.subheader("Price by categorical grade")
    grade_choice = st.selectbox("Group price by", ["cut", "color", "clarity"], index=2)
    fig5, ax5 = plt.subplots(figsize=(9, 4.5))
    sns.boxplot(data=fdf, x=grade_choice, y="price", order=CAT_ORDER[grade_choice],
                hue=grade_choice, palette="mako", legend=False, ax=ax5)
    ax5.set_title(f"Price distribution by {grade_choice}")
    st.pyplot(fig5)
    st.caption(
        "Counterintuitively, median price doesn't rise cleanly with 'better' cut/color/clarity grades ΓÇö "
        "that's because carat (size) dominates price and isn't held constant here. Higher-graded stones "
        "in this dataset also skew smaller, since large rough stones are harder to cut to top grades."
    )

# ---------------------------------------------------------------------------
# Tab 5 ΓÇö Correlation
# ---------------------------------------------------------------------------

with tabs[4]:
    st.subheader("Correlation heatmap (numeric features)")
    corr = fdf[num_cols].corr()
    fig6, ax6 = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax6)
    st.pyplot(fig6)
    st.caption(
        "x, y, z, and carat are almost perfectly collinear (all measure size), so I treat them as one "
        "signal rather than four independent features. Depth and table are nearly uncorrelated with "
        "price ΓÇö they describe cut proportions, not size, and matter far less to price than carat does."
    )

st.divider()
st.caption("Built with pandas, seaborn, and Streamlit. Data cleaning steps documented in Tab 1.")
