import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings("ignore")

# === Load your dataset ===
df = pd.read_excel("salesForecast_model.xlsx")  # <-- your Qlik-exported file
df.rename(columns={"MonthYear": "Date", "Sum(Units_Sold)": "Units_Sold"}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])

# === Output setup ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_output = f"sales_forecast_by_model_{timestamp}.xlsx"
chart_folder = f"charts_{timestamp}"
os.makedirs(chart_folder, exist_ok=True)

writer = pd.ExcelWriter(excel_output, engine='openpyxl')

# === Forecast per model ===
for model_name in df['Model'].unique():
    model_df = df[df['Model'] == model_name].copy()
    model_df.set_index('Date', inplace=True)
    model_df = model_df.asfreq('MS')
    model_df['Units_Sold'].fillna(0, inplace=True)

    try:
        model = SARIMAX(model_df['Units_Sold'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        results = model.fit(disp=False)

        forecast = results.get_forecast(steps=12)
        forecast_index = pd.date_range(start=model_df.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')
        forecast_df = forecast.summary_frame()
        forecast_df = forecast_df[['mean', 'mean_ci_lower', 'mean_ci_upper']]
        forecast_df.columns = ['Forecasted_Units_Sold', 'Lower_CI', 'Upper_CI']
        forecast_df['Model'] = model_name
        forecast_df.index = forecast_index
        forecast_df.index.name = 'Forecast_Month'

        # Save forecast to Excel
        forecast_df.reset_index().to_excel(writer, sheet_name=model_name[:31], index=False)

        # === Plot chart ===
        plt.figure(figsize=(12, 6))
        plt.plot(model_df.index, model_df['Units_Sold'], label='Actual', color='blue')
        plt.plot(forecast_df.index, forecast_df['Forecasted_Units_Sold'], label='Forecast', color='orange')
        plt.fill_between(forecast_df.index,
                         forecast_df['Lower_CI'],
                         forecast_df['Upper_CI'],
                         color='orange', alpha=0.3, label='Confidence Interval')
        plt.title(f"Sales Forecast for {model_name}")
        plt.xlabel("Date")
        plt.ylabel("Units Sold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Save chart image
        chart_path = os.path.join(chart_folder, f"{model_name}_forecast.png")
        plt.savefig(chart_path)
        plt.close()

    except Exception as e:
        print(f"⚠️ Forecast failed for {model_name}: {e}")

# Save all Excel sheets
writer.close()

print(f"✅ Forecast tables saved to: {excel_output}")
print(f"✅ Forecast charts saved to folder: {chart_folder}")
