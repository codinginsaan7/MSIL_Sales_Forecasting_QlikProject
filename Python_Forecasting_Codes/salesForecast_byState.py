import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings("ignore")

# === Load and clean data ===
df = pd.read_excel("salesForecast_state.xlsx")
df.rename(columns={
    "MonthYear": "Date", 
    "Sum(Net_Revenue)": "Revenue", 
    "Sum(Units_Sold)": "Units_Sold"
}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
df['Units_Sold'] = pd.to_numeric(df['Units_Sold'], errors='coerce')
df['Revenue_scaled'] = df['Revenue'] / 100000  # Scale for model stability

# === Setup output ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_output = f"forecast_revenue_units_state_{timestamp}.xlsx"
chart_folder = f"forecast_charts_state_{timestamp}"
os.makedirs(chart_folder, exist_ok=True)
writer = pd.ExcelWriter(excel_output, engine='openpyxl')

# === Forecast loop per state ===
for region in df['State'].unique():
    region_df = df[df['State'] == region].copy()
    region_df.set_index('Date', inplace=True)
    region_df = region_df.asfreq('MS')
    region_df['Revenue_scaled'].fillna(0, inplace=True)
    region_df['Units_Sold'].fillna(0, inplace=True)

    try:
        # Revenue Forecast
        rev_model = SARIMAX(region_df['Revenue_scaled'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        rev_result = rev_model.fit(disp=False)
        revenue_forecast = rev_result.get_forecast(steps=12)
        revenue_mean = revenue_forecast.predicted_mean * 100000

        # Units Sold Forecast
        unit_model = SARIMAX(region_df['Units_Sold'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        unit_result = unit_model.fit(disp=False)
        units_forecast = unit_result.get_forecast(steps=12)
        units_mean = units_forecast.predicted_mean

        # Build forecast DataFrame
        future_index = pd.date_range(region_df.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')
        forecast_df = pd.DataFrame({
            'Forecast_Month': future_index,
            'Forecasted_Revenue': revenue_mean.values,
            'Forecasted_Units_Sold': units_mean.values,
            'Region': region
        })

        forecast_df.to_excel(writer, sheet_name=region[:31], index=False)

        # === Plot Revenue Forecast ===
        plt.figure(figsize=(12, 6))
        plt.plot(region_df.index, region_df['Revenue_scaled'] * 100000, label='Actual Revenue', color='blue')
        plt.plot(future_index, revenue_mean, label='Forecast Revenue', color='green')
        plt.title(f"Net Revenue Forecast - {region}")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{chart_folder}/{region}_revenue_forecast.png")
        plt.close()

        # === Plot Units Sold Forecast ===
        plt.figure(figsize=(12, 6))
        plt.plot(region_df.index, region_df['Units_Sold'], label='Actual Units Sold', color='purple')
        plt.plot(future_index, units_mean, label='Forecast Units Sold', color='orange')
        plt.title(f"Units Sold Forecast - {region}")
        plt.xlabel("Month")
        plt.ylabel("Units Sold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{chart_folder}/{region}_units_forecast.png")
        plt.close()

    except Exception as e:
        print(f"⚠️ Forecast failed for {region}: {e}")

# Save workbook
writer.close()
print(f"✅ Forecast saved to: {excel_output}")
print(f"📊 Charts saved to: {chart_folder}")
