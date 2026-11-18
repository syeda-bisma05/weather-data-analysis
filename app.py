import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import quote

st.set_page_config(page_title="Weather Data Dashboard", page_icon="⛅", layout="wide")

SKY = "#4A90C2"
NAVY = "#1F3A5F"
SUN = "#F4A261"

# ---------- Soft clouds in the background ----------
CLOUDS = """<svg xmlns='http://www.w3.org/2000/svg' width='1400' height='360' viewBox='0 0 1400 360'>
<g fill='white' opacity='0.8'>
<circle cx='160' cy='110' r='38'/><circle cx='205' cy='90' r='52'/><circle cx='260' cy='112' r='40'/><rect x='125' y='110' width='170' height='42' rx='21'/>
<circle cx='700' cy='70' r='30'/><circle cx='735' cy='55' r='42'/><circle cx='780' cy='72' r='32'/><rect x='672' y='70' width='140' height='34' rx='17'/>
<circle cx='1130' cy='140' r='40'/><circle cx='1175' cy='118' r='55'/><circle cx='1235' cy='142' r='42'/><rect x='1090' y='140' width='190' height='44' rx='22'/>
<circle cx='430' cy='230' r='26'/><circle cx='460' cy='218' r='36'/><circle cx='498' cy='232' r='28'/><rect x='404' y='230' width='122' height='30' rx='15'/>
</g></svg>"""
cloud_url = "data:image/svg+xml," + quote(CLOUDS)

CSS = """
<style>
.stApp {
    background-image: url("CLOUD_URL"), linear-gradient(180deg, #d6ebf8 0%, #eaf4fb 40%, #f8fbfe 100%);
    background-repeat: no-repeat, no-repeat;
    background-size: 100% 380px, 100% 100%;
    background-position: top center, center;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.75); }
h1, h2, h3 { color: #1F3A5F; }
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.85);
    border-left: 6px solid #4A90C2;
    border-radius: 12px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(31, 58, 95, 0.12);
}
[data-testid="stMetricValue"] { color: #1F3A5F; }
</style>
""".replace("CLOUD_URL", cloud_url)
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Load and clean data ----------
@st.cache_data
def load_data():
    raw = pd.read_csv("weather_data.csv")
    raw = raw.drop_duplicates()
    df = raw.copy()
    df["Formatted Date"] = pd.to_datetime(df["Formatted Date"], format="%m/%d/%Y")
    cols = ["Formatted Date", "Precip Type", "Temperature (C)",
            "Apparent Temperature (C)", "Wind Speed (km/h)",
            "Visibility (km)", "Pressure (millibars)", "Humidity",
            "Month", "Year"]
    df = df[cols].sort_values("Formatted Date", kind="stable").reset_index(drop=True)
    df["Precip Type"] = df["Precip Type"].ffill().bfill()
    for c in ["Pressure (millibars)", "Humidity", "Visibility (km)"]:
        df[c] = df[c].replace(0, np.nan).ffill().bfill()
    return df


df = load_data()


def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, color=NAVY, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)


def show(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ---------- Title ----------
st.title("⛅ Historical Weather Data Dashboard")
st.write("Explore 11 years (2006 to 2016) of hourly weather data. "
         "Use the filters on the left to change the numbers and graphs.")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
all_types = sorted(df["Precip Type"].unique())
types = st.sidebar.multiselect("Precipitation type", all_types, default=all_types)

min_d = df["Formatted Date"].min().date()
max_d = df["Formatted Date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_d, max_d),
                                   min_value=min_d, max_value=max_d)
if len(date_range) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()
start, end = date_range

filtered = df[
    df["Precip Type"].isin(types)
    & (df["Formatted Date"] >= pd.to_datetime(start))
    & (df["Formatted Date"] <= pd.to_datetime(end))
]
if filtered.empty:
    st.warning("No data for these filters. Please change them.")
    st.stop()

# ---------- Key numbers ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average temperature", f"{filtered['Temperature (C)'].mean():.1f} C")
c2.metric("Highest temperature", f"{filtered['Temperature (C)'].max():.1f} C")
c3.metric("Average humidity", f"{filtered['Humidity'].mean():.2f}")
c4.metric("Number of days", f"{filtered['Formatted Date'].nunique():,}")

st.write("")

# ---------- Graphs ----------
left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("**Q1. How is temperature distributed, and what is the typical value?**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered["Temperature (C)"], bins=40, kde=True, color=SKY, ax=ax)
        style_ax(ax, "Distribution of Temperature", "Temperature (C)", "Count")
        show(fig)
        st.caption("Observation: Temperature is roughly bell-shaped, with a typical value of about 12 C.")

with right:
    with st.container(border=True):
        st.markdown("**Q2. How is wind speed distributed, and are there extreme values?**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered["Wind Speed (km/h)"], bins=40, color=SUN, ax=ax)
        style_ax(ax, "Distribution of Wind Speed", "Wind Speed (km/h)", "Count")
        show(fig)
        st.caption("Observation: Most hours have wind below 15 km/h, and a few extreme values go up to about 64 km/h.")

left1, right1 = st.columns(2)

with left1:
    with st.container(border=True):
        st.markdown("**Q3. How often does each precipitation type (rain or snow) occur?**")
        counts = filtered["Precip Type"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=counts.index, y=counts.values, color=SKY, ax=ax)
        style_ax(ax, "Precipitation Type Count", "Precipitation type", "Count")
        show(fig)
        st.caption("Observation: Rain is far more common than snow (about 89% of hours compared to 11%).")

with right1:
    with st.container(border=True):
        st.markdown("**Q4. What is the relationship between temperature and humidity?**")
        sample = filtered.sample(min(3000, len(filtered)), random_state=42)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x="Temperature (C)", y="Humidity", data=sample,
                        alpha=0.4, color=SKY, ax=ax)
        style_ax(ax, "Temperature vs Humidity", "Temperature (C)", "Humidity")
        show(fig)
        st.caption("Observation: There is a negative relationship (about -0.64): as temperature rises, humidity tends to fall.")

left2, right2 = st.columns(2)

with left2:
    with st.container(border=True):
        st.markdown("**Q5. How does the average temperature change across months?**")
        month_avg = filtered.groupby("Month")["Temperature (C)"].mean()
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.barplot(x=month_avg.index, y=month_avg.values, color=SKY, ax=ax)
        style_ax(ax, "Average Temperature by Month", "Month (1 = January)",
                 "Average Temperature (C)")
        show(fig)
        st.caption("Observation: Temperature peaks in July and August and is lowest in December and January.")

with right2:
    with st.container(border=True):
        st.markdown("**Extra: Which variables are related to each other?**")
        corr_cols = ["Temperature (C)", "Apparent Temperature (C)", "Wind Speed (km/h)",
                     "Humidity", "Pressure (millibars)", "Visibility (km)"]
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.heatmap(filtered[corr_cols].corr(), annot=True, fmt=".2f",
                    cmap="coolwarm", center=0, ax=ax, annot_kws={"size": 8})
        ax.set_title("Correlation Heatmap", color=NAVY, fontsize=12, fontweight="bold")
        plt.xticks(rotation=45, ha="right")
        show(fig)
        st.caption("Observation: Temperature and Apparent Temperature are almost perfectly correlated (0.99).")

with st.container(border=True):
    st.markdown("**Extra: How does temperature change over the years?**")
    monthly = filtered.set_index("Formatted Date")["Temperature (C)"].resample("MS").mean()
    fig, ax = plt.subplots(figsize=(12, 3.5))
    ax.plot(monthly.index, monthly.values, color=SKY, linewidth=2)
    ax.fill_between(monthly.index, monthly.values, color=SKY, alpha=0.15)
    ax.grid(alpha=0.3)
    style_ax(ax, "Average Monthly Temperature Over Time", "Date", "Average Temperature (C)")
    show(fig)
    st.caption("Observation: Temperature repeats the same yearly cycle every year, with warm summers and cold winters.")

# ---------- Raw data ----------
if st.checkbox("Show raw data table"):
    st.dataframe(filtered, use_container_width=True)

# ---------- Findings ----------
st.subheader("Main findings")
st.markdown(f"""
- **Temperature** is roughly bell-shaped with a typical value of about 12 C. It follows a clear yearly pattern, warmest in July and coldest in January.
- **Temperature and humidity** have a moderate negative relationship (about -0.64), so warmer hours tend to be drier.
- **Rain** is far more common than snow (about 89% of hours compared to 11%).
- **Wind speed** is right-skewed. Most hours are below 15 km/h, and the strongest winds (up to 63.85 km/h) are real storm events.
- The data was cleaned before use: duplicates were removed and impossible zero values in pressure, humidity and visibility were fixed.
- Current selection: **{len(filtered):,} hours** from **{start}** to **{end}**.
""")