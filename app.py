import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from databricks import sql
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor

# =========================================================
# 1. CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
TOKEN = os.getenv("DATABRICKS_TOKEN")

SILVER_TABLE = "sales.salesschema.silver_superstore"
GOLD_MONTHLY_TABLE = "sales.salesschema.gold_monthly_sales"

# =========================================================
# 2. PRODUCTION-STYLE THEME
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --canvas:#F3F6FC; --ink:#152742; --muted:#73839B; --line:#E3EAF4; --blue:#4778F5; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:linear-gradient(135deg,#F7F9FD 0%,#EFF4FB 100%); color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(243,246,252,.9); }
    .block-container { max-width:1680px; padding:1.25rem 2rem 3rem; }
    h1,h2,h3,h4 { font-family:'Manrope','DM Sans',sans-serif!important; letter-spacing:-.04em; color:var(--ink); }
    p { line-height:1.55; }

    /* SIDEBAR */
    [data-testid="stSidebar"] { background:#101B2D; border-right:1px solid #263853; }
    [data-testid="stSidebar"] > div:first-child { background:transparent; }
    [data-testid="stSidebar"] * { color:#EAF1FB; }
    [data-testid="stSidebar"] h2 { font:800 1.22rem 'Manrope',sans-serif!important; color:#fff!important; letter-spacing:-.03em; }
    [data-testid="stSidebar"] h3 { font:750 .9rem 'Manrope',sans-serif!important; color:#C5D7F0!important; letter-spacing:.02em; text-transform:uppercase; }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color:#DDE7F6!important; font-size:.82rem; font-weight:650; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:#8FA5C3!important; font-size:.75rem; line-height:1.6; }
    [data-testid="stSidebar"] hr { border-color:#2A3C56; margin:1.05rem 0; }
    [data-testid="stSidebar"] [data-baseweb="tag"] { background:#294C7D!important; border:1px solid #416AA4!important; border-radius:7px!important; }
    [data-testid="stSidebar"] [data-baseweb="tag"] span { color:#fff!important; font-weight:600; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] input { background:#17263C!important; border:1px solid #344965!important; border-radius:10px!important; color:#F8FAFF!important; min-height:42px; }
    [data-testid="stSidebar"] input { color:#F8FAFF!important; }
    [data-testid="stSidebar"] [data-baseweb="select"] svg { fill:#AFC4E1!important; }

    /* EXECUTIVE HEADER */
    .hero { position:relative; overflow:hidden; display:flex; flex-direction:column; justify-content:center; min-height:190px; background:linear-gradient(112deg,#101D33 0%,#18365E 58%,#2856A4 100%); padding:2rem 2.4rem; border-radius:22px; margin:0 0 1.45rem; border:1px solid rgba(255,255,255,.1); box-shadow:0 16px 38px rgba(24,48,84,.14); }
    .hero:after { content:""; position:absolute; width:290px; height:290px; right:-45px; top:-150px; border:1px solid rgba(255,255,255,.17); border-radius:50%; box-shadow:0 0 0 30px rgba(255,255,255,.035),0 0 0 65px rgba(255,255,255,.025); pointer-events:none; }
    .hero .eyebrow { display:inline-block; color:#A9D4FF!important; font-size:.68rem; font-weight:800; letter-spacing:.2em; margin-bottom:.6rem; }
    .hero h1 { color:#fff!important; font:800 clamp(1.8rem,2.7vw,2.45rem) 'Manrope',sans-serif!important; letter-spacing:-.055em; margin:0 0 .5rem; line-height:1.16; }
    .hero p { color:#D9E6F8!important; font-size:.91rem; max-width:780px; margin:0; line-height:1.7; }

    /* SECTION LABELS */
    .section-heading { display:flex; align-items:center; gap:.6rem; color:#172B49!important; font:800 1.22rem 'Manrope',sans-serif!important; letter-spacing:-.04em; margin:.35rem 0 .22rem; }
    .section-description { color:#71819A!important; font-size:.84rem; margin-bottom:.95rem; }

    /* KPI CARDS */
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"] { background:#fff; border:1px solid #E2E9F3; border-top:3px solid #4778F5; border-radius:15px; padding:1rem 1.05rem; min-height:120px; box-shadow:0 8px 22px rgba(22,43,73,.055); transition:transform .18s ease,box-shadow .18s ease; }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:hover { transform:translateY(-3px); box-shadow:0 14px 28px rgba(22,43,73,.1); }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(1) { border-top-color:#4778F5; }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(2) { border-top-color:#12A594; }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(3) { border-top-color:#8B6AE8; }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(4) { border-top-color:#E6A23C; }
    [data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(5) { border-top-color:#E36B8A; }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color:#75849A!important; font-size:.78rem; font-weight:700; }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color:#142640!important; font:800 clamp(1.05rem,1.45vw,1.5rem) 'Manrope',sans-serif!important; letter-spacing:-.045em; }

    /* CHART PANELS */
    [data-testid="stPlotlyChart"] { background:#fff; border:1px solid #E2EAF4; border-radius:16px; padding:.35rem; box-shadow:0 7px 24px rgba(23,43,73,.045); }
    [data-testid="stDataFrame"] { background:#fff; border:1px solid #E2EAF4; border-radius:13px; overflow:hidden; }
    [data-testid="stExpander"] { background:#fff; border:1px solid #E0E8F3; border-radius:12px; }
    [data-testid="stAlert"] { border-radius:12px; }

    /* BUTTONS */
    .stButton > button { border-radius:10px; min-height:42px; font-weight:700; border:1px solid #D8E2EF; transition:transform .15s ease,box-shadow .15s ease; }
    .stButton > button:hover { transform:translateY(-1px); box-shadow:0 6px 16px rgba(20,48,85,.12); }
    [data-testid="stSidebar"] .stButton > button { background:linear-gradient(135deg,#18A86B,#0D7A49)!important; color:#fff!important; border:1px solid #31BD83!important; border-radius:11px!important; min-height:48px; width:100%; font-weight:800; box-shadow:0 8px 20px rgba(13,122,73,.22); }
    [data-testid="stSidebar"] .stButton > button p { color:#fff!important; font-weight:800; }
    [data-testid="stSidebar"] .stButton > button:hover { background:linear-gradient(135deg,#15965D,#09683D)!important; box-shadow:0 10px 24px rgba(13,122,73,.3); }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap:.3rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { background:#1A2B43; border:1px solid #354C69; border-radius:9px; padding:.42rem .55rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:#147C4A!important; border-color:#36B87C!important; color:#fff!important; }
    hr { border-color:#E1E8F2!important; }
    .footer { color:#8190A6!important; font-size:.76rem; text-align:center; padding-top:1.25rem; line-height:1.9; }
    @media(max-width:1100px) { .block-container{padding:1.1rem 1.1rem 2.5rem}.hero{padding:1.8rem}.hero:after{opacity:.6} }
    @media(max-width:768px) { .block-container{padding:.8rem .7rem 2rem}.hero{padding:1.45rem 1.2rem;min-height:160px;border-radius:17px}.hero h1{font-size:1.65rem}.hero p{font-size:.84rem}[data-testid="stMetric"]{padding:.8rem;min-height:100px} }

    /* FLOATING SALES CHAT */
    .st-key-open_sales_chat {
        position: fixed !important;
        right: 24px !important;
        bottom: 22px !important;
        width: 64px !important;
        z-index: 100000 !important;
    }
    .st-key-open_sales_chat button {
        width: 60px !important;
        height: 60px !important;
        min-height: 60px !important;
        border-radius: 50% !important;
        background: #16804A !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 5px 20px rgba(0,0,0,.25) !important;
        font-size: 24px !important;
    }
    .st-key-sales_chat_popup {
        position: fixed !important;
        right: 24px !important;
        bottom: 96px !important;
        width: 360px !important;
        max-width: calc(100vw - 32px) !important;
        max-height: 70vh !important;
        overflow-y: auto !important;
        z-index: 99999 !important;
        background: #FFFFFF !important;
        border: 1px solid #DCE4EF !important;
        border-radius: 18px !important;
        padding: 16px !important;
        box-shadow: 0 8px 35px rgba(0,0,0,.22) !important;
    }
    .st-key-sales_chat_popup [data-testid="stChatMessage"] {
        padding: .5rem !important;
    }
    @media (max-width: 480px) {
        .st-key-open_sales_chat { right: 12px !important; bottom: 12px !important; }
        .st-key-sales_chat_popup {
            right: 12px !important;
            bottom: 82px !important;
            width: calc(100vw - 24px) !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 3. VALIDATE DATABRICKS CONFIGURATION
# =========================================================
if not SERVER_HOSTNAME or not HTTP_PATH or not TOKEN:
    st.error(
        "Databricks configuration is missing. "
        "Please check your .env file."
    )
    st.stop()

# =========================================================
# 4. DATABASE AND DISPLAY HELPERS
# =========================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_data(query):
    with sql.connect(
        server_hostname=SERVER_HOSTNAME,
        http_path=HTTP_PATH,
        access_token=TOKEN,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def sql_string(value):
    """Escape single quotes in SQL string values."""
    return "'" + str(value).replace("'", "''") + "'"


def answer_sales_question(question):
    """Answer supported retail questions using read-only, predefined SQL."""
    q = question.lower().strip()

    if any(term in q for term in ["total revenue", "total sales", "overall revenue"]):
        query = f"SELECT ROUND(COALESCE(SUM(Sales), 0), 2) AS Answer FROM {SILVER_TABLE}"
        df = load_data(query)
        value = float(df["Answer"].iloc[0] or 0)
        return f"Total revenue is ${value:,.2f}."

    if "total profit" in q or "overall profit" in q:
        query = f"SELECT ROUND(COALESCE(SUM(Profit), 0), 2) AS Answer FROM {SILVER_TABLE}"
        df = load_data(query)
        value = float(df["Answer"].iloc[0] or 0)
        return f"Total profit is ${value:,.2f}."

    if "highest profit" in q or "most profit" in q:
        query = f"""SELECT Region, ROUND(SUM(Profit), 2) AS Profit
                    FROM {SILVER_TABLE} GROUP BY Region ORDER BY Profit DESC LIMIT 1"""
        df = load_data(query)
        return f"{df['Region'].iloc[0]} generated the highest profit: ${float(df['Profit'].iloc[0]):,.2f}."

    if "lowest profit" in q:
        query = f"""SELECT Region, ROUND(SUM(Profit), 2) AS Profit
                    FROM {SILVER_TABLE} GROUP BY Region ORDER BY Profit ASC LIMIT 1"""
        df = load_data(query)
        return f"{df['Region'].iloc[0]} had the lowest profit: ${float(df['Profit'].iloc[0]):,.2f}."

    if any(term in q for term in ["losing money", "loss-making products", "loss making products", "products with losses"]):
        query = f"""SELECT Product_Name, ROUND(SUM(Profit), 2) AS Profit
                    FROM {SILVER_TABLE} GROUP BY Product_Name
                    HAVING SUM(Profit) < 0 ORDER BY Profit ASC LIMIT 10"""
        df = load_data(query)
        if df.empty:
            return "No loss-making products were found."
        return "Top loss-making products:\n\n" + df.to_string(index=False)

    if "category" in q and any(term in q for term in ["compare", "revenue", "profit"]):
        query = f"""SELECT Category, ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit FROM {SILVER_TABLE}
                    GROUP BY Category ORDER BY Revenue DESC"""
        return "Category performance:\n\n" + load_data(query).to_string(index=False)

    if "region" in q and any(term in q for term in ["revenue", "compare"]):
        query = f"""SELECT Region, ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit FROM {SILVER_TABLE}
                    GROUP BY Region ORDER BY Revenue DESC"""
        return "Regional performance:\n\n" + load_data(query).to_string(index=False)

    if "help" in q or "what can you do" in q:
        return ("Try: 'What is the total revenue?', 'What is the total profit?', "
                "'Which region has the highest profit?', 'Which products are losing money?', "
                "or 'Compare category revenue and profit.'")

    return ("I don't recognize that question yet. Try asking about total revenue, total profit, "
            "highest/lowest profit by region, loss-making products, category performance, "
            "or regional revenue.")


def section_heading(title, description):
    st.markdown(
        f"""
        <div class="section-heading">{title}</div>
        <div class="section-description">{description}</div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=None):
    fig.update_layout(
        template="plotly_white",
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#24364F",
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        title=dict(
            font=dict(size=17, color="#172B4D"),
            x=0.03,
            xanchor="left",
        ),
        margin=dict(l=25, r=25, t=70, b=35),
        xaxis=dict(
            tickfont=dict(size=11, color="#334155"),
            showgrid=False,
            zeroline=False,
            automargin=True,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#334155"),
            gridcolor="#E4EAF2",
            zeroline=False,
            automargin=True,
        ),
        hoverlabel=dict(
            bgcolor="#172B4D",
            font=dict(color="#FFFFFF", size=12),
        ),
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig


# =========================================================
# 5. LATEST-DATA FORECAST FUNCTION
# Forecasts from the full dataset, ignoring sidebar filters.
# =========================================================
def forecast_latest_sales(history_df, horizon):
    if history_df.empty:
        raise ValueError("No historical sales data was returned.")

    history_df = history_df.copy()
    history_df["Month"] = (
        pd.to_datetime(history_df["Month"])
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    history_df["Revenue"] = pd.to_numeric(
        history_df["Revenue"],
        errors="coerce",
    )
    history_df = history_df.dropna(
        subset=["Month", "Revenue"]
    )

    monthly = (
        history_df.groupby("Month")["Revenue"]
        .sum()
        .sort_index()
        .asfreq("MS", fill_value=0)
    )

    if len(monthly) < 8:
        raise ValueError(
            f"Only {len(monthly)} months of history are available. "
            "At least 8 months are required for forecasting."
        )

    features = pd.DataFrame(index=monthly.index)
    features["Month_Number"] = monthly.index.month
    features["Year"] = monthly.index.year
    features["Time_Index"] = range(len(monthly))
    features["Lag_1"] = monthly.shift(1)
    features["Lag_2"] = monthly.shift(2)
    features["Lag_3"] = monthly.shift(3)
    features["Rolling_Mean_3"] = monthly.shift(1).rolling(3).mean()

    feature_columns = [
        "Month_Number",
        "Year",
        "Time_Index",
        "Lag_1",
        "Lag_2",
        "Lag_3",
        "Rolling_Mean_3",
    ]

    training_data = features.dropna()
    if len(training_data) < 5:
        raise ValueError(
            "There is insufficient historical data to train the model."
        )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(
        training_data[feature_columns],
        monthly.loc[training_data.index],
    )

    history_values = list(monthly.astype(float).values)
    last_month = monthly.index.max()
    predictions = []

    for step in range(1, int(horizon) + 1):
        next_month = last_month + pd.DateOffset(months=step)
        input_row = pd.DataFrame(
            [{
                "Month_Number": next_month.month,
                "Year": next_month.year,
                "Time_Index": len(history_values),
                "Lag_1": history_values[-1],
                "Lag_2": history_values[-2],
                "Lag_3": history_values[-3],
                "Rolling_Mean_3": sum(history_values[-3:]) / 3,
            }]
        )

        predicted_revenue = max(
            0.0,
            float(model.predict(input_row[feature_columns])[0]),
        )
        predictions.append(
            {
                "Month": next_month,
                "Predicted_Revenue": predicted_revenue,
            }
        )

        # Use the previous prediction to forecast the following month.
        history_values.append(predicted_revenue)

    return pd.DataFrame(predictions), monthly
# =========================================================
# 6. PAGE HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">RETAIL INTELLIGENCE · EXECUTIVE WORKSPACE</div>
        <h1 style="word-spacing: 12px;">
    RETAIL SALES INTELLIGENCE PLATFORM
</h1>
        <p>
            One workspace for revenue, profitability, regional performance and product insights —
            powered by your Databricks sales data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 7. LOAD FILTER OPTIONS
# =========================================================
try:
    with st.spinner("Connecting to Databricks..."):
        date_df = load_data(
            f"""
            SELECT
                MIN(Order_Date) AS Min_Date,
                MAX(Order_Date) AS Max_Date
            FROM {SILVER_TABLE}
            """
        )

        if (
            date_df.empty
            or pd.isna(date_df["Min_Date"].iloc[0])
            or pd.isna(date_df["Max_Date"].iloc[0])
        ):
            st.warning("No sales data is available.")
            st.stop()

        min_date = pd.to_datetime(
            date_df["Min_Date"].iloc[0]
        ).date()

        max_date = pd.to_datetime(
            date_df["Max_Date"].iloc[0]
        ).date()

        region_options_df = load_data(
            f"""
            SELECT DISTINCT Region
            FROM {SILVER_TABLE}
            WHERE Region IS NOT NULL
            ORDER BY Region
            """
        )

        available_regions = (
            region_options_df["Region"].dropna().tolist()
        )

        category_options_df = load_data(
            f"""
            SELECT DISTINCT Category
            FROM {SILVER_TABLE}
            WHERE Category IS NOT NULL
            ORDER BY Category
            """
        )

        available_categories = (
            category_options_df["Category"].dropna().tolist()
        )

except Exception as e:
    st.error("Unable to load filter options from Databricks.")
    st.exception(e)
    st.stop()

# =========================================================
# 8. SIDEBAR FILTERS AND FORECAST CONTROLS
# =========================================================
with st.sidebar:
    st.markdown("## ◈ Retail Intelligence")
    st.caption("YOUR SALES COMMAND CENTER")
    st.divider()

    st.markdown("### 01 · ANALYTICS FILTERS")

    selected_dates = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="analytics_date_range",
    )

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        elif len(selected_dates) == 1:
            start_date = end_date = selected_dates[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = selected_dates

    selected_regions = st.multiselect(
        "Select region",
        options=available_regions,
        default=[],
        placeholder="Choose region(s)...",
        key="analytics_regions",
        help="These selections affect actual sales analytics only.",
    )

    selected_categories = st.multiselect(
        "Select category",
        options=available_categories,
        default=[],
        placeholder="Choose category(s)...",
        key="analytics_categories",
        help="These selections affect actual sales analytics only.",
    )

    st.divider()
    st.markdown("### 02 · FORECAST STUDIO")

    st.caption(
        "Forecasts use the full historical dataset and are independent "
        "of the date, region, and category filters above."
    )

    forecast_horizon = st.radio(
        "Predict future sales?",
        options=[1, 2, 3],
        index=2,
        horizontal=True,
        format_func=lambda n: (
            f"{n} month" if n == 1 else f"{n} months"
        ),
        key="latest_forecast_horizon",
    )

    predict_clicked = st.button(
        "🔮 Predict Sales",
        type="primary",
        use_container_width=True,
        key="predict_latest_button",
    )

    st.divider()
    st.caption("CONNECTED DATA PLATFORM")
    st.markdown("**Databricks SQL**")
    st.caption("Delta Lake · Silver and Gold")

    if st.button(
        "↻ Refresh dashboard",
        use_container_width=True,
        key="refresh_dashboard",
    ):
        st.cache_data.clear()
        st.rerun()

# =========================================================
# 9. ACTUAL SALES FILTER CONDITIONS
# =========================================================
analytics_ready = bool(
    selected_regions and selected_categories
)

if analytics_ready:
    where_conditions = [
        f"Order_Date >= DATE '{start_date.isoformat()}'",
        f"Order_Date < DATE_ADD(DATE '{end_date.isoformat()}', 1)",
    ]

    region_values = ", ".join(
        sql_string(region) for region in selected_regions
    )

    category_values = ", ".join(
        sql_string(category) for category in selected_categories
    )

    where_conditions.append(
        f"Region IN ({region_values})"
    )

    where_conditions.append(
        f"Category IN ({category_values})"
    )

    where_clause = "WHERE " + " AND ".join(where_conditions)

    # =====================================================
    # 10. LOAD ACTUAL ANALYTICS FROM DATABRICKS
    # =====================================================
    try:
        with st.spinner("Loading actual sales analytics..."):
            kpi_df = load_data(
                f"""
                SELECT
                    ROUND(COALESCE(SUM(Sales), 0), 2) AS Revenue,
                    ROUND(COALESCE(SUM(Profit), 0), 2) AS Profit,
                    COALESCE(SUM(Quantity), 0) AS Units_Sold,
                    COUNT(DISTINCT Order_ID) AS Total_Orders
                FROM {SILVER_TABLE}
                {where_clause}
                """
            )

            revenue = float(kpi_df["Revenue"].iloc[0] or 0)
            profit = float(kpi_df["Profit"].iloc[0] or 0)
            units = int(kpi_df["Units_Sold"].iloc[0] or 0)
            orders = int(kpi_df["Total_Orders"].iloc[0] or 0)

            profit_margin = (
                profit / revenue * 100
                if revenue != 0
                else 0
            )

            monthly_df = load_data(
                f"""
                SELECT
                    DATE_TRUNC('MONTH', Order_Date) AS Month,
                    ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit
                FROM {SILVER_TABLE}
                {where_clause}
                GROUP BY DATE_TRUNC('MONTH', Order_Date)
                ORDER BY Month
                """
            )

            region_df = load_data(
                f"""
                SELECT
                    Region,
                    ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit
                FROM {SILVER_TABLE}
                {where_clause}
                GROUP BY Region
                ORDER BY Revenue DESC
                """
            )

            category_df = load_data(
                f"""
                SELECT
                    Category,
                    ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit
                FROM {SILVER_TABLE}
                {where_clause}
                GROUP BY Category
                ORDER BY Revenue DESC
                """
            )

            product_df = load_data(
                f"""
                SELECT
                    Product_Name,
                    ROUND(SUM(Sales), 2) AS Revenue,
                    ROUND(SUM(Profit), 2) AS Profit,
                    SUM(Quantity) AS Units_Sold
                FROM {SILVER_TABLE}
                {where_clause}
                GROUP BY Product_Name
                ORDER BY Revenue DESC
                LIMIT 10
                """
            )

    except Exception as e:
        st.error("Unable to load actual sales analytics.")
        st.exception(e)
        st.stop()

    # =====================================================
    # 11. KPI CARDS
    # =====================================================
    section_heading(
        "Business overview",
        "Actual sales performance for your selected filters.",
    )

    st.caption(
        f"Reporting period: {start_date:%d %b %Y} – "
        f"{end_date:%d %b %Y}"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Revenue", f"${revenue:,.2f}")
    col2.metric("Total Profit", f"${profit:,.2f}")
    col3.metric("Profit Margin", f"{profit_margin:.2f}%")
    col4.metric("Total Orders", f"{orders:,}")
    col5.metric("Units Sold", f"{units:,}")

    # =====================================================
    # 12. MONTHLY REVENUE TREND
    # =====================================================
    st.divider()

    section_heading(
        "Sales performance",
        "Monitor actual monthly revenue and identify trends.",
    )

    monthly_df["Month"] = pd.to_datetime(
        monthly_df["Month"],
        errors="coerce",
    )

    monthly_df["Revenue"] = pd.to_numeric(
        monthly_df["Revenue"],
        errors="coerce",
    )

    monthly_df["Profit"] = pd.to_numeric(
        monthly_df["Profit"],
        errors="coerce",
    )

    monthly_df = (
        monthly_df
        .dropna(subset=["Month", "Revenue"])
        .sort_values("Month")
    )

    if monthly_df.empty:
        st.info(
            "No monthly sales data is available for the selected filters."
        )
    else:
        fig_monthly = px.line(
            monthly_df,
            x="Month",
            y="Revenue",
            markers=True,
            title="Monthly actual revenue",
            labels={
                "Month": "Month",
                "Revenue": "Revenue ($)",
            },
        )

        fig_monthly.update_traces(
            line=dict(color="#3568B0", width=3),
            marker=dict(size=7, color="#234F8A"),
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Revenue: $%{y:,.2f}<extra></extra>"
            ),
        )

        style_chart(fig_monthly)

        st.plotly_chart(
            fig_monthly,
            use_container_width=True,
        )

    # =====================================================
    # 13. MONTH-OVER-MONTH REVENUE GROWTH
    # =====================================================
    section_heading(
        "Monthly revenue growth",
        "Compare actual revenue with the previous month.",
    )

    monthly_df["Previous_Month_Revenue"] = (
        monthly_df["Revenue"].shift(1)
    )

    previous_revenue = (
        monthly_df["Previous_Month_Revenue"].where(
            monthly_df["Previous_Month_Revenue"] != 0
        )
    )

    monthly_df["MoM_Growth"] = (
        (
            monthly_df["Revenue"]
            - monthly_df["Previous_Month_Revenue"]
        )
        / previous_revenue
    ) * 100

    growth_df = monthly_df.dropna(
        subset=["MoM_Growth"]
    ).copy()

    if growth_df.empty:
        st.info(
            "At least two months with non-zero previous-month revenue "
            "are required to calculate growth."
        )
    else:
        fig_growth = px.bar(
            growth_df,
            x="Month",
            y="MoM_Growth",
            title="Month-over-month revenue growth",
            labels={
                "Month": "Month",
                "MoM_Growth": "Growth (%)",
            },
        )

        fig_growth.add_hline(
            y=0,
            line_dash="dash",
            line_color="#64748B",
        )

        fig_growth.update_traces(
            marker_color="#4776C5",
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Growth: %{y:.2f}%<extra></extra>"
            ),
        )

        style_chart(fig_growth)

        st.plotly_chart(
            fig_growth,
            use_container_width=True,
        )

    with st.expander("View monthly growth details"):
        growth_table = monthly_df[
            [
                "Month",
                "Revenue",
                "Previous_Month_Revenue",
                "MoM_Growth",
            ]
        ].copy()

        growth_table["Month"] = (
            growth_table["Month"].dt.strftime("%b %Y")
        )

        growth_table = growth_table.rename(
            columns={
                "Revenue": "Revenue ($)",
                "Previous_Month_Revenue": "Previous Revenue ($)",
                "MoM_Growth": "Growth (%)",
            }
        )

        st.dataframe(
            growth_table.round(2),
            use_container_width=True,
            hide_index=True,
        )
    # =====================================================
    # 14. REGIONAL PERFORMANCE
    # =====================================================
    st.divider()

    section_heading(
        "Regional performance",
        "Compare actual revenue and profitability across regions.",
    )

    if region_df.empty:
        st.info("No regional data is available for these filters.")
    else:
        region_df["Revenue"] = pd.to_numeric(
            region_df["Revenue"], errors="coerce"
        )

        region_df["Profit"] = pd.to_numeric(
            region_df["Profit"], errors="coerce"
        )

        region_df["Profit_Margin"] = (
            region_df["Profit"]
            / region_df["Revenue"].where(region_df["Revenue"] != 0)
        ) * 100

        region_col1, region_col2 = st.columns(2)

        with region_col1:
            fig_region = px.bar(
                region_df.sort_values("Revenue"),
                x="Revenue",
                y="Region",
                orientation="h",
                title="Revenue by region",
                labels={
                    "Region": "Region",
                    "Revenue": "Revenue ($)",
                },
                hover_data=["Profit"],
            )

            fig_region.update_traces(
                marker_color="#3568B0",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Revenue: $%{x:,.2f}<extra></extra>"
                ),
            )

            style_chart(fig_region)

            st.plotly_chart(
                fig_region,
                use_container_width=True,
            )

        with region_col2:
            fig_margin = px.bar(
                region_df.sort_values("Profit_Margin"),
                x="Profit_Margin",
                y="Region",
                orientation="h",
                title="Profit margin by region",
                labels={
                    "Region": "Region",
                    "Profit_Margin": "Profit margin (%)",
                },
                hover_data=["Revenue", "Profit"],
            )

            fig_margin.update_traces(
                marker_color="#16804A",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Profit margin: %{x:.2f}%<extra></extra>"
                ),
            )

            style_chart(fig_margin)

            st.plotly_chart(
                fig_margin,
                use_container_width=True,
            )

    # =====================================================
    # 15. CATEGORY PERFORMANCE
    # =====================================================
    st.divider()

    section_heading(
        "Category analysis",
        "Identify the categories generating the most actual revenue.",
    )

    if category_df.empty:
        st.info("No category data is available for these filters.")
    else:
        fig_category = px.bar(
            category_df.sort_values(
                "Revenue",
                ascending=False,
            ),
            x="Category",
            y="Revenue",
            title="Revenue by category",
            labels={
                "Category": "Category",
                "Revenue": "Revenue ($)",
            },
            hover_data=["Profit"],
        )

        fig_category.update_traces(
            marker_color="#6C63C7",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Revenue: $%{y:,.2f}<extra></extra>"
            ),
        )

        style_chart(fig_category)

        st.plotly_chart(
            fig_category,
            use_container_width=True,
        )

    # =====================================================
    # 16. TOP 10 PRODUCTS
    # =====================================================
    st.divider()

    section_heading(
        "Top-performing products",
        "Explore the ten products generating the highest actual revenue.",
    )

    if product_df.empty:
        st.info("No product data is available for these filters.")
    else:
        fig_products = px.bar(
            product_df.sort_values(
                "Revenue",
                ascending=True,
            ),
            x="Revenue",
            y="Product_Name",
            orientation="h",
            title="Top 10 products by revenue",
            labels={
                "Product_Name": "Product",
                "Revenue": "Revenue ($)",
            },
            hover_data=["Profit", "Units_Sold"],
        )

        fig_products.update_traces(
            marker_color="#3568B0",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Revenue: $%{x:,.2f}<extra></extra>"
            ),
        )

        style_chart(fig_products, height=560)

        st.plotly_chart(
            fig_products,
            use_container_width=True,
        )

        with st.expander("View top-product details"):
            product_table = product_df.rename(
                columns={
                    "Product_Name": "Product",
                    "Revenue": "Revenue ($)",
                    "Profit": "Profit ($)",
                    "Units_Sold": "Units sold",
                }
            )

            st.dataframe(
                product_table.round(2),
                use_container_width=True,
                hide_index=True,
            )

else:
    st.divider()

    section_heading(
        "Actual sales analytics",
        "Choose your filters to explore your actual sales data.",
    )

    st.info(
        "Select at least one region and one category in the left sidebar "
        "to display the actual sales KPIs, trends, regional analysis, "
        "category performance, and top products. The forecast is independent "
        "of these filters."
    )

# =========================================================
# 17. LATEST-DATA FORECAST
# Independent of date, region, and category filters.
# =========================================================
st.divider()

section_heading(
    "Latest sales forecast",
    "Predict future monthly revenue using all historical sales available "
    "in Databricks.",
)

st.caption(
    "Forecasts use the full dataset, including all regions and categories. "
    "The analytics date range does not restrict the forecasting history."
)

# Generate a new forecast only after clicking the button.
if predict_clicked:
    try:
        with st.spinner(
            "Training the model using all available historical sales..."
        ):
            full_history_df = load_data(
                f"""
                SELECT
                    DATE_TRUNC('MONTH', Order_Date) AS Month,
                    SUM(Sales) AS Revenue
                FROM {SILVER_TABLE}
                GROUP BY DATE_TRUNC('MONTH', Order_Date)
                ORDER BY Month
                """
            )

            forecast_df, historical_monthly = forecast_latest_sales(
                full_history_df,
                forecast_horizon,
            )

            # Save the generated forecast in the current session.
            st.session_state["latest_sales_forecast_result"] = (
                forecast_df
            )

            st.session_state["latest_sales_forecast_horizon"] = (
                forecast_horizon
            )

            st.session_state["latest_sales_forecast_data_end"] = (
                historical_monthly.index.max()
            )

    except Exception as e:
        st.session_state.pop(
            "latest_sales_forecast_result",
            None,
        )

        st.session_state.pop(
            "latest_sales_forecast_horizon",
            None,
        )

        st.session_state.pop(
            "latest_sales_forecast_data_end",
            None,
        )

        st.error("Unable to generate the sales forecast.")
        st.exception(e)

# Show forecast results only if they match the selected horizon.
saved_horizon = st.session_state.get(
    "latest_sales_forecast_horizon"
)

saved_forecast = st.session_state.get(
    "latest_sales_forecast_result"
)

if (
    saved_forecast is not None
    and saved_horizon == forecast_horizon
):
    forecast_display_df = saved_forecast.copy()

    forecast_display_df["Month"] = pd.to_datetime(
        forecast_display_df["Month"]
    )

    forecast_display_df["Month_Label"] = (
        forecast_display_df["Month"].dt.strftime("%B %Y")
    )

    last_data_month = pd.to_datetime(
        st.session_state["latest_sales_forecast_data_end"]
    ).strftime("%B %Y")

    st.success(
        f"Forecast generated successfully. Historical data is available "
        f"through {last_data_month}."
    )

    # Display the selected number of forecast KPI cards.
    forecast_cards = st.columns(forecast_horizon)

    for index, (_, row) in enumerate(
        forecast_display_df.iterrows()
    ):
        forecast_cards[index].metric(
            row["Month_Label"],
            f"${float(row['Predicted_Revenue']):,.2f}",
        )

    # Forecast chart.
    fig_forecast = px.bar(
        forecast_display_df,
        x="Month_Label",
        y="Predicted_Revenue",
        title=f"Revenue forecast: next {forecast_horizon} month(s)",
        labels={
            "Month_Label": "Forecast month",
            "Predicted_Revenue": "Predicted revenue ($)",
        },
        text="Predicted_Revenue",
    )

    fig_forecast.update_traces(
        marker_color="#16804A",
        texttemplate="$%{y:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Predicted revenue: $%{y:,.2f}<extra></extra>"
        ),
    )

    style_chart(fig_forecast)

    st.plotly_chart(
        fig_forecast,
        use_container_width=True,
    )

    # Forecast details.
    forecast_table = forecast_display_df[
        ["Month_Label", "Predicted_Revenue"]
    ].rename(
        columns={
            "Month_Label": "Forecast month",
            "Predicted_Revenue": "Predicted revenue ($)",
        }
    )

    forecast_table["Predicted revenue ($)"] = (
        forecast_table["Predicted revenue ($)"].round(2)
    )

    st.dataframe(
        forecast_table,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Forecasts are model estimates, not actual sales. They are generated "
        "from all available historical sales and are not affected by the "
        "date, region, or category selections used for analytics."
    )

elif saved_forecast is not None:
    st.info(
        "You changed the forecast horizon. Click the green button in the "
        "sidebar again to generate the selected number of months."
    )

else:
    st.info(
        "Choose 1, 2, or 3 months in the left sidebar and click "
        "'Predict latest months' when you are ready. No predictions are "
        "generated automatically."
    )
# =========================================================
# 18. FLOATING SALES CHATBOT
# =========================================================

if "show_sales_chat" not in st.session_state:
    st.session_state["show_sales_chat"] = False

if "sales_chat_history" not in st.session_state:
    st.session_state["sales_chat_history"] = [
        {
            "role": "assistant",
            "content": (
                "Hi! 👋 I'm your Sales Assistant. Ask me about revenue, "
                "profit, regions, categories, or loss-making products. "
                "Type 'help' for examples."
            ),
        }
    ]

# Floating button: stays visible while the page scrolls.
if st.button(
    "💬",
    key="open_sales_chat",
    help="Open Sales Assistant",
):
    st.session_state["show_sales_chat"] = (
        not st.session_state["show_sales_chat"]
    )

# Show the floating chat window when opened.
if st.session_state["show_sales_chat"]:
    with st.container(key="sales_chat_popup"):
        st.markdown("### 💬 Sales Assistant")
        st.caption("Retail Sales Intelligence")

        if st.button("✕ Close chat", key="close_sales_chat"):
            st.session_state["show_sales_chat"] = False
            st.rerun()

        # Display the conversation.
        for message in st.session_state["sales_chat_history"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Message input and Send button.
        with st.form(
            "floating_sales_chat_form",
            clear_on_submit=True,
        ):
            question = st.text_input(
                "Message",
                placeholder="Ask about your sales...",
                label_visibility="collapsed",
            )

            send = st.form_submit_button(
                "Send",
                use_container_width=True,
            )

        if send and question.strip():
            st.session_state["sales_chat_history"].append(
                {
                    "role": "user",
                    "content": question.strip(),
                }
            )

            try:
                response = answer_sales_question(question)
            except Exception:
                response = (
                    "I couldn't retrieve the data from Databricks. "
                    "Please try again."
                )

            st.session_state["sales_chat_history"].append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

            st.rerun()


# =========================================================
# 19. FOOTER
# =========================================================
st.divider()

st.markdown(
    """
    <div class="footer">
        Retail Sales Intelligence Platform<br>
        Powered by Databricks · Delta Lake · Python · Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)