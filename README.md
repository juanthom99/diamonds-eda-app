# Diamonds Dataset — EDA Streamlit App

A Streamlit app that loads the `diamonds.csv` dataset (53,940 round-cut
diamonds), cleans it, and walks through a full exploratory data analysis:
structure, distributions, outliers, and relationships with price.

## Dataset

`data/diamonds.csv` — 10 columns: `carat`, `cut`, `color`, `clarity`, `depth`,
`table`, `price`, `x`, `y`, `z`. Source: the standard seaborn example dataset
(originally from ggplot2).

## Setup

```bash
# from inside this folder
uv add streamlit pandas numpy matplotlib seaborn
uv run streamlit run app.py
```

(Or with plain pip: `pip install -r requirements.txt` then
`streamlit run app.py`.)

The app opens at `http://localhost:8501`.

## What's in the app

- **Tab 1 — Overview & Cleaning**: shape, dtypes, missing-value check, and
  the cleaning steps applied (146 exact duplicates dropped, 20 rows with a
  0mm dimension dropped, a few rows with implausible 20mm+ dimensions
  dropped as likely data-entry typos). No columns were dropped — every
  field carries independent signal.
- **Tab 2 — Distributions**: histogram + boxplot for any numeric column,
  skewness callout, and count plots for the three categorical grades
  (cut, color, clarity).
- **Tab 3 — Outliers**: IQR-based outlier table across all numeric columns,
  plus a carat-vs-price scatterplot with price outliers highlighted (kept
  in the data — they're real large/high-clarity stones, not errors).
- **Tab 4 — Relationships with Price**: carat vs. price colored by clarity,
  and price distribution by cut/color/clarity.
- **Tab 5 — Correlation**: heatmap across numeric features, with a note on
  the near-collinearity of carat/x/y/z.

All charts respond to the carat/cut/color filters in the sidebar.

## Screenshots

![Overview tab](screenshots/overview.png)
![Overview tab, continued](screenshots/overview2.png)
![Distributions tab](screenshots/distribution.png)
![Distributions tab, continued](screenshots/distribution2.png)
![Relationships tab](screenshots/relationship.png)
![Relationships tab, continued](screenshots/relationship2.png)

## Notes

- Data cleaning removes duplicates and physically impossible measurements
  (e.g. a diamond with 0mm depth) rather than silently reindexing — the
  cleaning log is shown in the app itself, not just in this README.
- The 4 Cs (carat, cut, color, clarity) are treated as ordered categorical
  variables so plots and comparisons respect their natural grade order.
