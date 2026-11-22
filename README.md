# Weather Data Analysis

This project analyzes and visualizes historical hourly weather data (2006 to 2016) using Python and Streamlit.

## Live Dashboard
https://weather-data-analysis-ajgmpzhobzmn69b9eaqbmt.streamlit.app/

## Dataset
Historical hourly weather data from Kaggle (saved as `weather_data.csv`). It has 96,453 rows with Temperature, Apparent Temperature, Humidity, Wind Speed, Visibility, Pressure and Precipitation Type.

## What was done
- Data cleaning: missing values, duplicates and outliers (including zero values in pressure, humidity and visibility)
- Univariate analysis: distributions of temperature, wind speed and precipitation type
- Bivariate analysis: correlation heatmap, temperature vs humidity, average temperature by month
- Interactive Streamlit dashboard with sidebar filters (precipitation type and date range)

## Key findings
- Temperature follows a clear yearly pattern: warmest in July and August, coldest in December and January.
- Temperature and humidity have a negative relationship (about -0.64).
- Temperature and apparent temperature are almost perfectly correlated (0.99).
- Rain is far more common than snow.

## Files
- `app.py`: Streamlit dashboard
- `weather_analysis.ipynb`: analysis notebook
- `weather_data.csv`: dataset
- `requirements.txt`: required libraries

## Run locally
pip install -r requirements.txt
streamlit run app.py
