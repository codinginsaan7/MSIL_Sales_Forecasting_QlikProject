import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings("ignore")

# === Load & clean the dataset ===
df = pd.read_excel("salesForecasting_ByModelandRevenue.xlsx")  # <-- Your file
df.rename(columns={"MonthYear": "Date", "Sum(Net_Revenue)": "Revenue"}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
df['Revenue_scaled'] = df['Revenue'] / 100000  # Scale down for modeling

# === Setup output paths ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_output = f"revenue_forecast_with_ci_{timestamp}.xlsx"
chart_folder = f"revenue_forecast_charts_with_ci_{timestamp}"
os.makedirs(chart_folder, exist_ok=True)

writer = pd.ExcelWriter(excel_output, engine='openpyxl')

# === Forecast per model ===
for model_name in df['Model'].unique():
    model_df = df[df['Model'] == model_name].copy()
    model_df.set_index('Date', inplace=True)
    model_df = model_df.asfreq('MS')
    model_df['Revenue_scaled'].fillna(0, inplace=True)

    try:
        # Fit SARIMA model
        model = SARIMAX(model_df['Revenue_scaled'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        result = model.fit(disp=False)

        # Forecast 12 months
        future_index = pd.date_range(model_df.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')
        forecast = result.get_forecast(steps=12)
        forecast_ci = forecast.conf_int()
        forecast_mean = forecast.predicted_mean * 100000  # scale back
        lower_ci = forecast_ci.iloc[:, 0] * 100000
        upper_ci = forecast_ci.iloc[:, 1] * 100000

        # Create output DataFrame
        forecast_out = pd.DataFrame({
            'Forecast_Month': future_index,
            'Forecasted_Revenue': forecast_mean.values,
            'Lower_CI': lower_ci.values,
            'Upper_CI': upper_ci.values,
            'Model': model_name
        })

        # Save forecast to Excel
        forecast_out.to_excel(writer, sheet_name=model_name[:31], index=False)

        # === Plot ===
        plt.figure(figsize=(12, 6))
        plt.plot(model_df.index, model_df['Revenue_scaled'] * 100000, label='Actual', color='blue')
        plt.plot(future_index, forecast_mean, label='Forecast', color='green')
        plt.fill_between(future_index, lower_ci, upper_ci, color='green', alpha=0.2, label='Confidence Interval')
        plt.title(f"Net Revenue Forecast for {model_name}")
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(chart_folder, f"{model_name}_revenue_forecast_ci.png"))
        plt.close()

    except Exception as e:
        print(f"⚠️ Forecast failed for {model_name}: {e}")

# Finalize Excel
writer.close()
print(f"✅ Forecast with CI saved to: {excel_output}")
print(f"📊 Charts with CI saved to: {chart_folder}")

