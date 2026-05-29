# Sellers Dashboard

A Streamlit dashboard for exploring seller performance data.

## Features

- **Region filter** to slice the entire dashboard.
- **KPI metrics**: seller count, units sold, total sales, and average sales.
- **Sellers table** with a CSV download of the filtered rows.
- **Charts** for Units Sold, Total Sales, and Sales Average — grouped by region or by top sellers.
- **Seller detail** view for any individual vendor.

## Run locally

```bash
pip install -r requirements.txt
streamlit run sellers_app.py
```

The app reads `sellers.xlsx` from the project root.
