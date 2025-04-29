import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import zipfile

warnings.filterwarnings("ignore")

# === Load dataset ===
df = pd.read_excel("salesForecast_dealer.xlsx")
df.rename(columns={"MonthYear": "Date", "Sum(Units_Sold)": "Units_Sold"}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'])
df['Units_Sold'] = pd.to_numeric(df['Units_Sold'], errors='coerce')

# === Output setup ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_output = f"sales_forecast_by_dealer_{timestamp}.xlsx"
chart_folder = f"dealer_forecast_charts_{timestamp}"
os.makedirs(chart_folder, exist_ok=True)
writer = pd.ExcelWriter(excel_output, engine='openpyxl')

# === Forecasting per dealer ===
for dealer in df['Dealer_ID'].dropna().unique():
    dealer_df = df[df['Dealer_ID'] == dealer].copy()
    dealer_df.set_index('Date', inplace=True)
    dealer_df = dealer_df.resample('MS').sum()
    dealer_df['Units_Sold'].fillna(0, inplace=True)

    try:
        model = SARIMAX(dealer_df['Units_Sold'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        result = model.fit(disp=False)

        future_index = pd.date_range(dealer_df.index[-1] + pd.DateOffset(months=1), periods=12, freq='MS')
        forecast = result.get_forecast(steps=12)
        forecast_mean = forecast.predicted_mean
        conf_int = forecast.conf_int()

        # Excel Output
        forecast_df = pd.DataFrame({
            'Forecast_Month': future_index,
            'Forecast_Units_Sold': forecast_mean.values,
            'Lower_CI': conf_int.iloc[:, 0].values,
            'Upper_CI': conf_int.iloc[:, 1].values,
            'Dealer_ID': dealer
        })
        forecast_df.to_excel(writer, sheet_name=dealer[:31], index=False)

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(dealer_df.index, dealer_df['Units_Sold'], label='Observed', color='blue')
        plt.plot(future_index, forecast_mean, label='Forecast', color='orange')
        plt.fill_between(future_index, conf_int.iloc[:, 0], conf_int.iloc[:, 1], color='orange', alpha=0.3)
        plt.title(f"Sales Forecast for {dealer}")
        plt.xlabel("Date")
        plt.ylabel("Units Sold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        chart_path = os.path.join(chart_folder, f"{dealer}_forecast.png")
        plt.savefig(chart_path)
        plt.close()

    except Exception as e:
        print(f"⚠️ Forecast failed for {dealer}: {e}")

# Save Excel
writer.close()

# === Zip charts folder ===
zip_name = f"{chart_folder}.zip"
with zipfile.ZipFile(zip_name, 'w') as zipf:
    for file in os.listdir(chart_folder):
        zipf.write(os.path.join(chart_folder, file), arcname=file)

print(f"✅ Forecast saved to: {excel_output}")
print(f"✅ Charts zipped at: {zip_name}")
