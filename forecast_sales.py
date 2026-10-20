
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =========================================================
# 1. CONFIGURATION
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "models" / "sales_forecast_model.joblib"

FORECAST_HORIZON = 3


# =========================================================
# 2. LOAD TRAINED MODEL
# =========================================================

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}\n"
            "Run 'python train_model.py' first."
        )

    artifact = joblib.load(MODEL_PATH)

    print("Trained model loaded successfully.")
    print(f"Model type: {artifact['model_name']}")
    print(f"Historical months: {artifact['historical_months']}")

    return artifact


# =========================================================
# 3. LOAD HISTORICAL REVENUE
# =========================================================

def load_historical_data():
    """
    Load monthly revenue from Databricks.

    Uses the same Gold table as the training script.
    """

    import os

    from databricks import sql
    from dotenv import load_dotenv

    load_dotenv()

    hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")

    if not hostname or not http_path or not token:
        raise ValueError(
            "Databricks configuration is missing. "
            "Check your .env file."
        )

    query = """
        SELECT
            Month,
            Revenue
        FROM sales.salesschema.gold_monthly_sales
        ORDER BY Month
    """

    print("\nConnecting to Databricks for historical data...")

    with sql.connect(
        server_hostname=hostname,
        http_path=http_path,
        access_token=token,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [
                column[0] for column in cursor.description
            ]

    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        raise ValueError(
            "No monthly revenue data was returned from Databricks."
        )

    df["Month"] = pd.to_datetime(
        df["Month"], utc=True
    ).dt.tz_localize(None)

    df["Month"] = (
        df["Month"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    df["Revenue"] = pd.to_numeric(
        df["Revenue"], errors="coerce"
    )

    df = df.dropna(subset=["Month", "Revenue"])

    # Ensure exactly one observation per month.
    df = (
        df.groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
        .reset_index(drop=True)
    )

    # Check that no calendar months are missing.
    expected_months = pd.date_range(
        start=df["Month"].min(),
        end=df["Month"].max(),
        freq="MS",
    )

    if not df["Month"].reset_index(drop=True).equals(
        pd.Series(expected_months, name="Month")
    ):
        raise ValueError(
            "The monthly data has missing or inconsistent months. "
            "Check the Gold table before forecasting."
        )

    return df


# =========================================================
# 4. PREPARE MODEL FEATURES
# =========================================================

def build_features(history):
    """
    Build the same features used during training.
    """

    month = history["Month"].iloc[-1] + pd.DateOffset(months=1)

    feature_row = {
        "Month_Number": month.month,
        "Year": month.year,
        "Time_Index": len(history),
        "Lag_1": history["Revenue"].iloc[-1],
        "Lag_2": history["Revenue"].iloc[-2],
        "Lag_3": history["Revenue"].iloc[-3],
        "Rolling_Mean_3": history["Revenue"].iloc[-3:].mean(),
    }

    return month, pd.DataFrame([feature_row])


# =========================================================
# 5. GENERATE THREE-MONTH FORECAST
# =========================================================

def generate_forecast(artifact, historical_df):
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    history = historical_df.copy()
    forecasts = []

    print("\nGenerating revenue forecast...")

    for _ in range(FORECAST_HORIZON):
        month, features = build_features(history)

        # Match the exact feature order used in training.
        features = features[feature_columns]

        predicted_revenue = float(
            model.predict(features)[0]
        )

        # Revenue cannot be negative in this forecasting output.
        predicted_revenue = max(0.0, predicted_revenue)

        forecasts.append({
            "Month": month,
            "Predicted_Revenue": round(
                predicted_revenue, 2
            ),
        })

        # Feed the prediction into history to forecast the
        # following month recursively.
        history = pd.concat(
            [
                history,
                pd.DataFrame({
                    "Month": [month],
                    "Revenue": [predicted_revenue],
                }),
            ],
            ignore_index=True,
        )

    return pd.DataFrame(forecasts)


# =========================================================
# 6. DISPLAY AND SAVE RESULTS
# =========================================================

def main():
    artifact = load_model()
    historical_df = load_historical_data()

    saved_last_month = pd.Timestamp(
        artifact["last_month"]
    ).to_period("M")

    current_last_month = historical_df["Month"].max().to_period("M")

    if saved_last_month != current_last_month:
        raise ValueError(
            "The saved model and current Gold table end in different "
            "months. Run 'python train_model.py' to retrain the model."
        )

    if len(historical_df) < 3:
        raise ValueError(
            "At least three historical months are required."
        )

    forecast_df = generate_forecast(
        artifact,
        historical_df,
    )

    print("\n" + "=" * 55)
    print("NEXT THREE MONTHS: REVENUE FORECAST")
    print("=" * 55)

    display_df = forecast_df.copy()
    display_df["Month"] = (
        display_df["Month"].dt.strftime("%B %Y")
    )

    display_df["Predicted_Revenue"] = (
        display_df["Predicted_Revenue"].map(
            lambda value: f"${value:,.2f}"
        )
    )

    print(display_df.to_string(index=False))

    output_path = PROJECT_DIR / "models" / "sales_forecast.csv"

    forecast_df.to_csv(output_path, index=False)

    print(f"\nForecast saved to: {output_path}")
    print("\nForecast completed successfully.")


if __name__ == "__main__":
    main()
