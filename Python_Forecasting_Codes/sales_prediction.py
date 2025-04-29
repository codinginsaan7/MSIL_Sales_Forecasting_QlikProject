import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt

# Step 1: Load and prepare the data
df = pd.read_excel("monthly_sales.xlsx")
df.rename(columns={'Sum(Units_Sold)': 'Units_Sold'}, inplace=True)
df['MonthYear'] = pd.to_datetime(df['MonthYear'], format='%b-%Y')
df.set_index('MonthYear', inplace=True)

# Step 2: Fit the SARIMA model
model = SARIMAX(df['Units_Sold'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
results = model.fit(disp=False)

# Step 3: Forecast next 12 months
forecast = results.get_forecast(steps=12)
forecast_df = forecast.summary_frame()
forecast_df = forecast_df[['mean', 'mean_ci_lower', 'mean_ci_upper']]
forecast_df.columns = ['Units_Sold', 'Lower_CI', 'Upper_CI']
forecast_df.index.name = 'MonthYear'

# Step 4: Combine historical and forecast data
df['Type'] = 'Observed'
forecast_df['Type'] = 'Forecast'
combined = pd.concat([df[['Units_Sold', 'Type']], forecast_df], axis=0)

# Step 5: Export to Excel
combined.to_excel("combined_sales_forecast.xlsx")
print("✅ Combined data saved to 'combined_sales_forecast.xlsx'.")

# Step 6: Plot
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Units_Sold'], label='Observed', color='blue')
plt.plot(forecast_df.index, forecast_df['Units_Sold'], label='Forecast', color='orange')
plt.fill_between(forecast_df.index, forecast_df['Lower_CI'], forecast_df['Upper_CI'],
                 color='orange', alpha=0.2, label='Confidence Interval')
plt.title("Sales Forecast vs Historical Data")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
