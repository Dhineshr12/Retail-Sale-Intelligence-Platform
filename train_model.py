
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from databricks import sql

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# =========================================================
# 1. CONFIGURATION
# =========================================================

load_dotenv()

SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
TOKEN = os.getenv("DATABRICKS_TOKEN")

GOLD_TABLE = "sales.salesschema.gold_monthly_sales"

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "sales_forecast_model.joblib"

FORECAST_HORIZON = 3
TEST_MONTHS = 6
RANDOM_STATE = 42


# =========================================================
# 2. CHECK DATABRICKS CONFIGURATION
# =========================================================

def validate_configuration():
    if not SERVER_HOSTNAME or not HTTP_PATH or not TOKEN:
        raise ValueError(
            "Databricks configuration is missing. "
            "Check DATABRICKS_SERVER_HOSTNAME, "
            "DATABRICKS_HTTP_PATH, and DATABRICKS_TOKEN "
            "in your .env file."
        )


# =========================================================
# 3. LOAD MONTHLY SALES FROM DATABRICKS
# =========================================================

def load_monthly_sales():
    query = f"""
        SELECT
            Month,
            Revenue
        FROM {GOLD_TABLE}
        ORDER BY Month
    """

    print("Connecting to Databricks...")

    with sql.connect(
        server_hostname=SERVER_HOSTNAME,
        http_path=HTTP_PATH,
        access_token=TOKEN,
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
            "The Gold monthly sales table returned no data."
        )

    df["Month"] = pd.to_datetime(df["Month"])
    df["Revenue"] = pd.to_numeric(
        df["Revenue"], errors="coerce"
    )

    df = df.dropna(subset=["Month", "Revenue"])

    # Normalize dates to the first day of each month.
    df["Month"] = (
        df["Month"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    # Ensure one row per month.
    df = (
        df.groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
        .reset_index(drop=True)
    )

    # A monthly forecasting model expects a continuous timeline.
    full_months = pd.date_range(
        start=df["Month"].min(),
        end=df["Month"].max(),
        freq="MS",
    )

    df = (
        df.set_index("Month")
        .reindex(full_months)
        .rename_axis("Month")
        .reset_index()
    )

    if df["Revenue"].isna().any():
        missing_months = df.loc[
            df["Revenue"].isna(), "Month"
        ].dt.strftime("%Y-%m").tolist()

        raise ValueError(
            "Some months have no recorded revenue: "
            f"{missing_months}. Check the source data before training."
        )

    if len(df) < 18:
        raise ValueError(
            f"Only {len(df)} monthly records are available. "
            "At least 18 continuous months are required "
            "for this training and evaluation setup."
        )

    print(f"Loaded {len(df)} monthly records.")
    print(
        f"Period: {df['Month'].min():%b %Y} "
        f"to {df['Month'].max():%b %Y}"
    )

    return df


# =========================================================
# 4. CREATE TIME-BASED FEATURES
# =========================================================

def create_features(df):
    data = df.copy()

    data["Month_Number"] = data["Month"].dt.month
    data["Year"] = data["Month"].dt.year

    # Time index captures the overall direction of the series.
    data["Time_Index"] = np.arange(len(data))

    # Previous months' revenue provides historical context.
    data["Lag_1"] = data["Revenue"].shift(1)
    data["Lag_2"] = data["Revenue"].shift(2)
    data["Lag_3"] = data["Revenue"].shift(3)

    # Rolling averages use past revenue, not the current target.
    data["Rolling_Mean_3"] = (
        data["Revenue"]
        .shift(1)
        .rolling(window=3)
        .mean()
    )

    return data


FEATURE_COLUMNS = [
    "Month_Number",
    "Year",
    "Time_Index",
    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Rolling_Mean_3",
]


# =========================================================
# 5. TRAIN AND EVALUATE THE MODEL
# =========================================================

def train_and_evaluate(df):
    feature_df = create_features(df).dropna().reset_index(
        drop=True
    )

    if len(feature_df) <= TEST_MONTHS:
        raise ValueError(
            "Not enough rows remain after creating lag features "
            "for the requested evaluation period."
        )

    train_df = feature_df.iloc[:-TEST_MONTHS].copy()
    test_df = feature_df.iloc[-TEST_MONTHS:].copy()

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["Revenue"]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["Revenue"]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
    )

    print("\nTraining Random Forest model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # MAPE can be misleading when actual values are near zero.
    nonzero_mask = y_test.to_numpy() != 0

    if nonzero_mask.any():
        mape = np.mean(
            np.abs(
                (
                    y_test.to_numpy()[nonzero_mask]
                    - predictions[nonzero_mask]
                )
                / y_test.to_numpy()[nonzero_mask]
            )
        ) * 100
    else:
        mape = None

    results = pd.DataFrame({
        "Month": test_df["Month"].values,
        "Actual_Revenue": y_test.to_numpy(),
        "Predicted_Revenue": predictions,
    })

    print("\nEvaluation results")
    print("-" * 55)
    print(f"Training rows: {len(train_df)}")
    print(f"Test months: {len(test_df)}")
    print(f"MAE:  ${mae:,.2f}")
    print(f"RMSE: ${rmse:,.2f}")

    if mape is not None:
        print(f"MAPE: {mape:.2f}%")
    else:
        print("MAPE: unavailable (all actual values are zero)")

    print("\nActual vs predicted revenue:")
    print(results.to_string(index=False))

    return model, results, mae, rmse, mape


# =========================================================
# 6. REFIT ON ALL DATA AND SAVE THE MODEL
# =========================================================

def save_model(df):
    feature_df = create_features(df).dropna().reset_index(
        drop=True
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
    )

    model.fit(
        feature_df[FEATURE_COLUMNS],
        feature_df["Revenue"],
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "last_month": df["Month"].max(),
        "historical_months": len(df),
        "forecast_horizon": FORECAST_HORIZON,
        "model_name": "RandomForestRegressor",
    }

    joblib.dump(artifact, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")
    print(
        "The saved model was refitted on all available "
        "historical feature rows."
    )


# =========================================================
# 7. MAIN EXECUTION
# =========================================================

def main():
    validate_configuration()

    monthly_sales = load_monthly_sales()

    # Evaluate on the last six months before saving.
    train_and_evaluate(monthly_sales)

    # Save a model trained on all available history.
    save_model(monthly_sales)

    print("\nModel training completed successfully.")


if __name__ == "__main__":
    main()
