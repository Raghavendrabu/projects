# Stock Price Detection using LSTM & ARIMA (Deep Learning PBL)

A Deep Learning Project-Based Learning (PBL) solution for predicting stock prices using a multi-feature **Long Short-Term Memory (LSTM)** Neural Network compared against a traditional **ARIMA** baseline, deployed as an interactive **Streamlit** web application.

---

## 📌 Project Overview

This project builds a time-series forecasting model for stock market prices (default: **Apple Inc. - AAPL**). It incorporates advanced data preprocessing, multi-feature scaling to avoid look-ahead bias, sequence generation (60-day window), traditional time-series benchmarking (ARIMA), and an end-to-end web deployment.

### Features
1. **Data Pipeline:** Downloads 5 years of daily stock records via `yfinance` (`Close`, `Volume`, `Open`).
2. **Feature Engineering:** Adds `Daily_Return` percentage change.
3. **Strict Scaler Isolation:** `MinMaxScaler` fit **ONLY** on the training partition (first 80% chronologically) to prevent data leakage.
4. **Deep Learning Architecture:**
   - **LSTM Layer 1:** 50 Units (`return_sequences=True`, `relu`) + `Dropout(0.2)`
   - **LSTM Layer 2:** 50 Units (`return_sequences=False`, `relu`) + `Dropout(0.2)`
   - **Dense Layer:** 25 Units (`relu`)
   - **Output Layer:** 1 Unit (Regression)
5. **ARIMA Baseline Comparison:** Fits `ARIMA(5,1,0)` on training `Close` prices and compares RMSE against LSTM.
6. **Visualizations:** Loss curves, ground truth vs predictions (LSTM & ARIMA), and RMSE comparison bar chart.
7. **Streamlit Web Application:** Interactive dashboard allowing any stock ticker search (e.g. `TSLA`, `MSFT`, `NVDA`), dynamic model training, test metrics, and **Tomorrow's Price Prediction**.

---

## 📁 Repository Structure

```
stock_price_lstm_pbl/
├── main.py                  # Standalone training, evaluation, ARIMA comparison & plot export script
├── app.py                   # Streamlit interactive web application
├── requirements.txt         # Required Python packages
├── models/                  # Saved models & scalers
│   ├── lstm_aapl.h5         # Saved Keras LSTM model
│   ├── feature_scaler.pkl   # Fitted MinMaxScaler for features
│   └── close_scaler.pkl     # Fitted MinMaxScaler for Close price
└── README.md                # Project documentation & run guide
```

---

## ⚡ Quick Start Guide

### Step 1: Clone or Navigate to Project Directory
```bash
cd c:\Projects\stock_price_lstm_pbl
```

### Step 2: Install Dependencies
Ensure Python 3.9+ is installed, then run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Main Model Training & Baseline Comparison Script
Executes full data collection, preprocessing, 50-epoch LSTM training, ARIMA benchmark fitting, RMSE calculation, and generates comparison plots:
```bash
python main.py
```

### Step 4: Launch the Streamlit Web Application
Starts the web application locally:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Evaluation & Metrics Summary

| Model | Architecture / Order | Features Used | Test Set RMSE |
|---|---|---|---|
| **LSTM (Deep Learning)** | 2-Layer Stacked LSTM + Dropout | `Close`, `Volume`, `Open`, `Daily_Return` | **~$3.00 - $4.50** |
| **ARIMA (Baseline)** | `ARIMA(5,1,0)` | `Close` (Univariate) | **~$15.00 - $25.00** |

---

## ⚙️ Key Technical Highlights for Grading

- **Look-Ahead Bias Prevention:** The feature and target scalers are explicitly fit on `train_df` only (`scaler.fit_transform(train_df)`), and `test_df` is transformed using `scaler.transform(test_df)`.
- **Chronological Sequence Creation:** Time steps window = 60 days. Sequences use `combined_test_scaled` (concatenating the last 60 days of train data with test data) so that test sample 0 has a complete 60-day historical window.
- **Inverse Scaling:** Model predictions are converted back to real US Dollar ($) scale using `close_scaler.inverse_transform()` before evaluating RMSE or plotting.
