# Sales Forecasting and Predictive Analytics Project

This project focuses on sales forecasting, predictive analytics, and dashboard visualization using **Qlik Sense**, **Qlik Catalog**, and **Python** (SARIMA models).

---

## 🚀 Project Structure

| Layer| File | Purpose |
|------|------|---------|
| Data Loading | `Stage1_MarutiSales.qvf` | Load historical datasets and store them as `.qvd` files |
| Forecasted Data Loading | `Predicted Sales.qvf` | Load forecasted results from Python (VS Code) and store them as `.qvd` files |
| Data Transformation | `Stage2_MarutiSales.qvf` | Merge, clean, and transform historical + forecasted data |
| Visualization | `Stage3_MarutiSales.qvf` | Final app: Binary loaded transformed data and built creative and interactive dashboards |

---

## 🛠️ Tools & Technologies Used
- Qlik Sense
- Qlik Catalog
- Python (SARIMA - Seasonal ARIMA)
- Qlik Master Calendar
- Set Analysis and Advanced Qlik Load Scripting

---

## 📊 Key Highlights
- Forecasted units sold and net revenue per **model**, **state**, and **dealer**.
- Achieved an average **forecast accuracy of 93%** (MAPE: 5–7%).
- Designed interactive dashboards to compare **historical vs forecasted** results across multiple dimensions.
- Streamlined business insights for data-driven decision-making.

---

## 📂 Folder Structure

Sales_Forecasting_Qlik_Project/
│
├── Qlik_Files/                         # All Qlik Sense project files (.qvf)
│   ├── Stage1_MarutiSales.qvf          # Stage 1: Load and save data into QVDs
│   ├── Stage2_MarutiSales.qvf          # Stage 2: Data transformation & preparation
│   ├── Stage3_MarutiSales.qvf          # Stage 3: Final dashboard visualizations
│   ├── Predicted_Sales.qvf             # Loading ML forecasted results into Qlik
│
├── Python_Forecasting_Codes/           # Python codes for sales forecasting (SARIMA models)
│   ├── salesPrediction_model.py        # Predicted Units Sold per Model
|   ├── salesPrediction_modelRevenue.py # Predicted Revenue per Model
│   ├── salesForecast_byState.py        # Forecasted Units Sold and Revenue per State
│   ├── salesForecast_byDealers.py      # Forecasted Units Sold per Dealer
│
├── Datasets_Used/                      # datasets that were used in the project
│   ├── customers.xlsx                  # dataset about customers
│   ├── dealers.xlsx                    # dataset about dealers
│   ├── inventory.xlsx                  # dataset about inventory
│   ├── sales.xlsx                      # dataset about sales
│
├── Dashboard_Screenshots/              # Images of the dashboards that were created
│
├── LICENSE                             # MIT License file
├── README.md                           # Full project documentation

## ⚠️ Disclaimer
Original datasets are confidential and not uploaded to maintain data privacy.  
Sample anonymized datasets are provided purely for demonstration purposes.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
Feel free to use, modify, and share the project with appropriate credit.
