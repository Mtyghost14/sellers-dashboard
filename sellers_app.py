from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "sellers.xlsx"

st.set_page_config(page_title="Sellers Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE)
    df["SELLER"] = df["NAME"].str.strip() + " " + df["LASTNAME"].str.strip()
    return df


df = load_data()

st.title("📊 Sellers Dashboard")
st.caption(f"{len(df)} sellers across {df['REGION'].nunique()} regions")

# --- Sidebar filters ---
st.sidebar.header("Filters")
regions = sorted(df["REGION"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

filtered = df[df["REGION"].isin(selected_regions)] if selected_regions else df.iloc[0:0]

# --- KPI metrics ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Sellers", len(filtered))
m2.metric("Units Sold", f"{int(filtered['SOLD UNITS'].sum()):,}")
m3.metric("Total Sales", f"{int(filtered['TOTAL SALES'].sum()):,}")
avg = filtered["SALES AVERAGE"].mean() if len(filtered) else 0
m4.metric("Avg. Sales", f"{avg:.3f}")

st.divider()

# --- Table ---
with st.container(border=True):
    st.subheader("Sellers Table")
    st.dataframe(
        filtered[
            ["REGION", "ID", "SELLER", "INCOME", "SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"]
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download filtered data (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="sellers_filtered.csv",
        mime="text/csv",
    )

st.divider()

# --- Charts ---
st.subheader("Charts")
metric_label = st.radio(
    "Metric",
    ["SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"],
    horizontal=True,
)
view = st.radio("Group by", ["By Region", "By Seller (top 15)"], horizontal=True)

if len(filtered):
    if view == "By Region":
        agg = (
            filtered.groupby("REGION")[metric_label]
            .sum() if metric_label != "SALES AVERAGE"
            else filtered.groupby("REGION")[metric_label].mean()
        ).reset_index()
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X("REGION:N", sort="-y", title="Region"),
                y=alt.Y(f"{metric_label}:Q", title=metric_label.title()),
                color=alt.Color("REGION:N", legend=None),
                tooltip=["REGION", metric_label],
            )
        )
    else:
        top = filtered.nlargest(15, metric_label)
        chart = (
            alt.Chart(top)
            .mark_bar()
            .encode(
                x=alt.X(f"{metric_label}:Q", title=metric_label.title()),
                y=alt.Y("SELLER:N", sort="-x", title="Seller"),
                color=alt.Color("REGION:N", title="Region"),
                tooltip=["SELLER", "REGION", metric_label],
            )
        )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data for the selected filters.")

st.divider()

# --- Single seller detail ---
with st.container(border=True):
    st.subheader("Seller Detail")
    if len(filtered):
        seller = st.selectbox(
            "Select a seller",
            filtered["SELLER"].sort_values().tolist(),
        )
        row = filtered[filtered["SELLER"] == seller].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Region", row["REGION"])
        c1.metric("ID", int(row["ID"]))
        c2.metric("Income", f"{int(row['INCOME']):,}")
        c2.metric("Units Sold", f"{int(row['SOLD UNITS']):,}")
        c3.metric("Total Sales", f"{int(row['TOTAL SALES']):,}")
        c3.metric("Sales Average", f"{row['SALES AVERAGE']:.3f}")
    else:
        st.info("No sellers to show.")
