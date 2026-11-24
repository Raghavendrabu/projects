"""
===============================================================================
Project Title: Stock Price Detection using LSTM vs ARIMA (Deep Learning PBL)
Author: Senior Data Scientist & Deep Learning Engineer
Target Ticker: Apple Inc. (AAPL)
Date Range: 2020-01-01 to 2025-01-01
===============================================================================

Instructions to Run:
1. Ensure dependencies are installed:
   pip install -r requirements.txt
2. Run this training and evaluation script:
   python main.py
3. Launch the Streamlit Web Application:
   streamlit run app.py
===============================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from statsmodels.tsa.arima.model import ARIMA
import joblib

# Fix random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)


# =============================================================================
# 1. DATA COLLECTION
# =============================================================================
def fetch_stock_data(ticker="AAPL", start_date="2020-01-01", end_date="2025-01-01"):
    """
    Downloads 5 years of historical stock data from Yahoo Finance.
    Cleans MultiIndex column headers if present.
    """
    print(f"\n[1/6] Downloading stock data for {ticker} ({start_date} to {end_date})...")
    df = yf.download(ticker, start=start_date, end=end_date)

    # Flatten MultiIndex columns if returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure required features exist
    required_cols = ['Close', 'Volume', 'Open']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required feature: {col}")

    # Remove any missing rows
    df = df.dropna().copy()
    print(f"Data successfully fetched. Shape: {df.shape}")
    print(df[['Open', 'Close', 'Volume']].head())
    return df


# =============================================================================
# 2. ADVANCED PREPROCESSING & FEATURE ENGINEERING
# =============================================================================
def preprocess_stock_data(df, time_steps=60, train_ratio=0.8):
    """
    1. Feature Engineering: Adds Daily_Return (percentage change).
    2. Chronological Split: 80% train, 20% test (NO SHUFFLE).
    3. MinMax Scaling: Fits scaler ONLY on train set to prevent look-ahead bias.
    4. Sequence Creation: Uses past `time_steps` days to predict next day's Close.
    """
    print("\n[2/6] Performing Advanced Preprocessing & Feature Engineering...")

    # Feature Engineering: Daily Return (% Change)
    df['Daily_Return'] = df['Close'].pct_change()
    # Fill first row's NaN percentage change with 0
    df['Daily_Return'] = df['Daily_Return'].fillna(0)

    # Define Feature matrix & Target
    feature_cols = ['Close', 'Volume', 'Open', 'Daily_Return']
    target_col = 'Close'
    target_idx = feature_cols.index(target_col)

    # Chronological Train-Test Split (80% Train, 20% Test)
    train_size = int(len(df) * train_ratio)
    train_df = df.iloc[:train_size][feature_cols].copy()
    test_df = df.iloc[train_size:][feature_cols].copy()
    test_dates = df.index[train_size:]

    print(f"Total dataset length: {len(df)} days")
    print(f"Training split: {len(train_df)} days (80%)")
    print(f"Testing split:  {len(test_df)} days (20%)")

    # Scale Data: FIT ONLY ON TRAIN DATA
    feature_scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = feature_scaler.fit_transform(train_df)
    test_scaled = feature_scaler.transform(test_df)

    # Dedicated Scaler for Target (Close Price) for easy inverse transform
    close_scaler = MinMaxScaler(feature_range=(0, 1))
    close_scaler.fit(train_df[[target_col]])

    # Helper function to construct 3D sequence arrays for LSTM: (samples, time_steps, features)
    def create_sequences(data, target_data, steps):
        X, y = [], []
        for i in range(steps, len(data)):
            X.append(data[i - steps:i, :])
            y.append(target_data[i])
        return np.array(X), np.array(y)

    # Build Training Sequences
    X_train, y_train = create_sequences(train_scaled, train_scaled[:, target_idx], time_steps)

    # Build Testing Sequences: Prepend last `time_steps` days of train set to test set
    combined_test_scaled = np.vstack([train_scaled[-time_steps:], test_scaled])
    target_combined = combined_test_scaled[:, target_idx]

    X_test, y_test = create_sequences(combined_test_scaled, target_combined, time_steps)

    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape:  {X_test.shape}, y_test shape:  {y_test.shape}")

    return {
        'X_train': X_train, 'y_train': y_train,
        'X_test': X_test, 'y_test': y_test,
        'train_df': train_df, 'test_df': test_df,
        'test_dates': test_dates,
        'feature_scaler': feature_scaler,
        'close_scaler': close_scaler
    }


# =============================================================================
# 3. LSTM MODEL BUILDING
# =============================================================================
def build_lstm_model(input_shape):
    """
    Builds Sequential LSTM model matching exact architecture:
    - Layer 1: LSTM(50, return_sequences=True, activation='relu') + Dropout(0.2)
    - Layer 2: LSTM(50, return_sequences=False, activation='relu') + Dropout(0.2)
    - Dense Layer: Dense(25, activation='relu')
    - Output Layer: Dense(1)
    """
    print("\n[3/6] Building LSTM Neural Network Architecture...")
    model = Sequential([
        LSTM(units=50, return_sequences=True, activation='relu', input_shape=input_shape),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False, activation='relu'),
        Dropout(0.2),
        Dense(units=25, activation='relu'),
        Dense(units=1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()
    return model


# =============================================================================
# 4. MODEL TRAINING & EVALUATION (LSTM & ARIMA)
# =============================================================================
def train_and_eval_lstm(model, preprocessed_data, epochs=50, batch_size=32):
    """
    Trains LSTM model for `epochs` and computes RMSE on unscaled actual prices.
    """
    print(f"\n[4/6] Training LSTM Model for {epochs} Epochs...")
    X_train = preprocessed_data['X_train']
    y_train = preprocessed_data['y_train']
    X_test = preprocessed_data['X_test']
    y_test = preprocessed_data['y_test']
    close_scaler = preprocessed_data['close_scaler']

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        verbose=1
    )

    # Predict on Test Set
    y_pred_scaled = model.predict(X_test)

    # Inverse transform predictions & actual test values back to real dollar values
    y_pred_actual = close_scaler.inverse_transform(y_pred_scaled)
    y_test_actual = close_scaler.inverse_transform(y_test.reshape(-1, 1))

    # Calculate RMSE
    rmse_lstm = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
    print(f"\n>>> LSTM Test RMSE: ${rmse_lstm:.4f}")

    return history, y_pred_actual, y_test_actual, rmse_lstm


def train_and_eval_arima(train_close, test_close, order=(5, 1, 0)):
    """
    Trains traditional ARIMA baseline model on training Close prices and predicts test set.
    """
    print("\n[5/6] Fitting Traditional ARIMA Baseline Model...")
    try:
        model = ARIMA(train_close, order=order)
        model_fit = model.fit()

        # Forecast test set horizon
        forecast = model_fit.forecast(steps=len(test_close))
        rmse_arima = np.sqrt(mean_squared_error(test_close, forecast))
        print(f">>> ARIMA Test RMSE: ${rmse_arima:.4f}")
        return forecast, rmse_arima
    except Exception as e:
        print(f"ARIMA fitting warning: {e}. Falling back to simple naive model for ARIMA comparison.")
        # Fallback naive forecast (last known value constant)
        forecast = np.full(len(test_close), train_close[-1])
        rmse_arima = np.sqrt(mean_squared_error(test_close, forecast))
        return forecast, rmse_arima


# =============================================================================
# 5. VISUALIZATIONS
# =============================================================================
def create_visualizations(history, y_test_actual, lstm_pred, arima_pred, rmse_lstm, rmse_arima, test_dates):
    """
    Generates required plots:
    Plot 1: Training vs Validation Loss over epochs
    Plot 2: Actual Test Prices vs LSTM Predicted Prices
    Plot 3: Actual Test Prices vs ARIMA Predicted Prices
    Plot 4: Bar chart comparing RMSE of LSTM vs ARIMA
    """
    print("\n[6/6] Generating Comparison Plots & Evaluation Dashboards...")

    # Set dark/modern aesthetic style for plots
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig = plt.figure(figsize=(16, 12))
    plt.suptitle("Deep Learning PBL: Stock Price Detection (LSTM vs ARIMA)", fontsize=16, fontweight='bold')

    # Plot 1: Training vs Validation Loss
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(history.history['loss'], label='Training Loss', color='#2b5c8f', linewidth=2)
    ax1.plot(history.history['val_loss'], label='Validation Loss', color='#e74c3c', linewidth=2)
    ax1.set_title("Plot 1: LSTM Training vs Validation Loss Over Epochs", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss (MSE)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Actual vs LSTM Predicted
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(test_dates, y_test_actual, label='Actual Price', color='#2c3e50', linewidth=1.5)
    ax2.plot(test_dates, lstm_pred, label=f'LSTM Forecast (RMSE: ${rmse_lstm:.2f})', color='#27ae60', linewidth=1.5)
    ax2.set_title("Plot 2: Actual Test Prices vs LSTM Predicted Prices", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Stock Price ($)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Actual vs ARIMA Predicted
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(test_dates, y_test_actual, label='Actual Price', color='#2c3e50', linewidth=1.5)
    ax3.plot(test_dates, arima_pred, label=f'ARIMA Forecast (RMSE: ${rmse_arima:.2f})', color='#e67e22', linestyle='--', linewidth=1.5)
    ax3.set_title("Plot 3: Actual Test Prices vs ARIMA Predicted Prices", fontsize=12, fontweight='bold')
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Stock Price ($)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Bar Chart Comparing RMSE
    ax4 = fig.add_subplot(2, 2, 4)
    models = ['LSTM (Deep Learning)', 'ARIMA (Traditional)']
    rmses = [rmse_lstm, rmse_arima]
    colors = ['#27ae60' if rmse_lstm < rmse_arima else '#e74c3c', '#e67e22']

    bars = ax4.bar(models, rmses, color=colors, width=0.4, edgecolor='black', linewidth=1)
    ax4.set_title("Plot 4: Model Performance Comparison (RMSE - Lower is Better)", fontsize=12, fontweight='bold')
    ax4.set_ylabel("RMSE ($)")

    # Add numeric labels on bars
    for bar in bars:
        height = bar.get_height()
        ax4.annotate(f'${height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5),
                     textcoords="offset points",
                     ha='center', va='bottom', fontweight='bold')

    ax4.set_ylim(0, max(rmses) * 1.25)
    ax4.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save visualization plot
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    plot_path = os.path.join(models_dir, "model_comparison_plots.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Plots saved to: {plot_path}")


# =============================================================================
# MAIN EXECUTION FLOW
# =============================================================================
def main():
    print("=" * 70)
    print(" STOCK PRICE DETECTION USING LSTM & ARIMA COMPARISON (PBL PROJECT)")
    print("=" * 70)

    ticker = "AAPL"
    start_date = "2020-01-01"
    end_date = "2025-01-01"
    time_steps = 60
    epochs = 50
    batch_size = 32

    # Step 1: Data Collection
    df = fetch_stock_data(ticker=ticker, start_date=start_date, end_date=end_date)

    # Step 2: Advanced Preprocessing
    data = preprocess_stock_data(df, time_steps=time_steps, train_ratio=0.8)

    # Step 3: Model Building
    input_shape = (data['X_train'].shape[1], data['X_train'].shape[2])
    lstm_model = build_lstm_model(input_shape=input_shape)

    # Step 4: Train & Evaluate LSTM
    history, lstm_pred, y_test_actual, rmse_lstm = train_and_eval_lstm(
        model=lstm_model,
        preprocessed_data=data,
        epochs=epochs,
        batch_size=batch_size
    )

    # Save trained LSTM model and scalers for Streamlit app reuse
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    try:
        lstm_model.save(os.path.join(models_dir, "lstm_aapl.keras"))
        print(f"Saved trained model to '{os.path.join(models_dir, 'lstm_aapl.keras')}'")
    except Exception as e:
        print(f"Keras save warning: {e}")
        lstm_model.save(os.path.join(models_dir, "lstm_aapl.h5"))
        print(f"Saved trained model to '{os.path.join(models_dir, 'lstm_aapl.h5')}'")
        
    joblib.dump(data['feature_scaler'], os.path.join(models_dir, "feature_scaler.pkl"))
    joblib.dump(data['close_scaler'], os.path.join(models_dir, "close_scaler.pkl"))
    print(f"Saved scalers to '{models_dir}'")

    # Step 5: Fit & Evaluate ARIMA Baseline Model
    train_close = data['train_df']['Close'].values
    test_close = data['test_df']['Close'].values
    arima_pred, rmse_arima = train_and_eval_arima(train_close=train_close, test_close=test_close)

    # Final Comparison Summary
    print("\n" + "=" * 70)
    print(" FINAL EVALUATION & MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(f" LSTM Model Test RMSE  : ${rmse_lstm:.4f}")
    print(f" ARIMA Model Test RMSE : ${rmse_arima:.4f}")
    diff = rmse_arima - rmse_lstm
    if diff > 0:
        pct_imp = (diff / rmse_arima) * 100
        print(f" CONCLUSION: LSTM outperforms ARIMA by ${diff:.2f} ({pct_imp:.1f}% reduction in RMSE).")
    else:
        print(f" CONCLUSION: ARIMA achieved lower RMSE by ${abs(diff):.2f}.")
    print("=" * 70)

    # Step 6: Create & Display Visualizations
    create_visualizations(
        history=history,
        y_test_actual=y_test_actual,
        lstm_pred=lstm_pred,
        arima_pred=arima_pred,
        rmse_lstm=rmse_lstm,
        rmse_arima=rmse_arima,
        test_dates=data['test_dates']
    )


if __name__ == "__main__":
    main()
