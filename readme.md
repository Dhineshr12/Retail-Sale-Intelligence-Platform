
# Retail Sales Intelligence Platform

An end-to-end retail analytics solution built using **Databricks, PySpark, Delta Lake, Databricks SQL, Python, and Streamlit**. This project transforms retail sales data into meaningful business insights through data engineering, interactive dashboards, machine learning-based sales forecasting, and a rule-based chatbot.

---

## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Dataset](#dataset)
- [Data Engineering Pipeline](#data-engineering-pipeline)
- [Databricks Tables](#databricks-tables)
- [Dashboard Features](#dashboard-features)
- [Sales Forecasting](#sales-forecasting)
- [Rule-Based Chatbot](#rule-based-chatbot)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Example Chatbot Questions](#example-chatbot-questions)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

The **Retail Sales Intelligence Platform** is an interactive business intelligence application designed to analyze retail sales, profitability, regional performance, product performance, and future sales trends.

The application uses Databricks for cloud-based data storage and processing. A **Bronze–Silver–Gold medallion architecture** organizes the data, while a Streamlit dashboard connects to Databricks SQL to display KPIs, visualizations, and sales insights.

The platform also includes a Random Forest regression model for monthly revenue forecasting and a rule-based chatbot for answering predefined sales-related questions.

## 🎯 Project Objectives

- Build a data engineering pipeline using Databricks and Delta Lake.
- Ingest, clean, and transform retail sales data.
- Implement the Bronze, Silver, and Gold data architecture.
- Create analytical tables for sales, regional, and product performance.
- Develop an interactive dashboard for business intelligence.
- Forecast monthly revenue using machine learning.
- Provide quick sales insights through a rule-based chatbot.
- Integrate data engineering, analytics, and machine learning into one application.

## ✨ Key Features

- **Executive KPI Dashboard:** Revenue, profit, profit margin, orders, and units sold.
- **Interactive Filters:** Filter supported analytics by date range, region, and category.
- **Monthly Revenue Analysis:** Visualize historical revenue trends.
- **Month-over-Month Growth:** Compare revenue across consecutive months.
- **Regional Performance:** Analyze revenue and profit margins by region.
- **Category Analysis:** Explore revenue by product category.
- **Product Performance:** Identify top-performing products.
- **Sales Forecasting:** Predict monthly revenue using Random Forest regression.
- **Model Evaluation:** Evaluate forecasts using MAE, RMSE, and MAPE.
- **Sales Chatbot:** Answer predefined sales questions using read-only SQL queries.
- **Databricks Integration:** Retrieve analytical data directly from Databricks SQL.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development and data processing |
| Databricks | Cloud data platform |
| PySpark | Data ingestion and transformation |
| Delta Lake | Reliable storage for structured data |
| Databricks SQL Warehouse | SQL query execution |
| Databricks SQL Connector | Connects Streamlit to Databricks |
| Streamlit | Interactive web dashboard |
| Pandas | Tabular data processing |
| Plotly | Interactive charts and visualizations |
| Scikit-learn | Machine learning and model evaluation |
| Random Forest Regressor | Monthly revenue forecasting |
| python-dotenv | Environment variable management |

## 🏗️ System Architecture

```text
                 Superstore.csv
                       |
                       v
              Databricks Volume
                       |
                       v
              +------------------+
              |  Bronze Layer    |
              |    Raw Data      |
              +------------------+
                       |
                       v
              +------------------+
              |  Silver Layer    |
              |  Cleaned Data    |
              +------------------+
                       |
                       v
              +------------------+
              |   Gold Layer     |
              | Aggregated Data  |
              +------------------+
                       |
                       v
              Databricks SQL Warehouse
                       |
                       v
              Databricks SQL Connector
                       |
                       v
              +----------------------+
              | Streamlit Dashboard  |
              +----------------------+
                    |          |
                    v          v
                Analytics   Chatbot

              Historical Sales Data
                       |
                       v
               Feature Engineering
                       |
                       v
              Random Forest Model
                       |
                       v
                Sales Forecasts
```

## 📊 Dataset

The project uses the **Sample Superstore** retail dataset, commonly distributed as `Superstore.csv`.

The dataset contains retail order information, including:

- Order dates
- Order identifiers
- Product names
- Product categories
- Regional information
- Sales revenue
- Profit
- Quantity sold

The dataset is uploaded to a Databricks Unity Catalog Volume.

**Databricks Volume Path:**

```text
/Volumes/sales/salesschema/retailsales/Superstore.csv
```

> **Note:** The dataset is used for educational and demonstration purposes. Ensure you have permission to use and redistribute your copy of the dataset.

## 🔄 Data Engineering Pipeline

The project follows the **Medallion Architecture**.

### 1. Bronze Layer — Raw Data

The original CSV data is ingested into a Delta table. This layer serves as the starting point for downstream transformations.

**Table:**

`sales.salesschema.bronze_superstore`

### 2. Silver Layer — Cleaned Data

The Silver layer prepares the raw data for reliable analysis.

Processing includes:

- Standardizing column names.
- Converting columns to appropriate data types.
- Parsing order dates.
- Handling invalid or inconsistent values.
- Preparing numerical fields for analysis.

**Table:**

`sales.salesschema.silver_superstore`

The development Silver table was verified to contain **9,994 rows**.

### 3. Gold Layer — Business Aggregations

The Gold layer contains analytical tables designed for dashboard reporting.

| Table | Description |
|---|---|
| `gold_monthly_sales` | Monthly revenue aggregation |
| `gold_product_performance` | Product-level performance metrics |
| `gold_regional_performance` | Regional sales and profitability |

## 🗄️ Databricks Tables

The application uses the following tables:

```text
sales.salesschema.bronze_superstore
sales.salesschema.silver_superstore
sales.salesschema.gold_monthly_sales
sales.salesschema.gold_product_performance
sales.salesschema.gold_regional_performance
```

### Data Validation Results

The following metrics were recorded during development:

| Metric | Value |
|---|---:|
| Total Revenue | 2,297,200.86 |
| Total Profit | 286,397.02 |
| Units Sold | 37,873 |
| Orders | 5,009 |
| Silver Records | 9,994 |
| Monthly Aggregated Records | 48 |

The monthly sales data covers **January 2014 to December 2017**.

These values are reference results from the development dataset. Results may differ if the source data or transformation logic changes.

## 📈 Dashboard Features

### 1. Executive KPI Dashboard

The dashboard displays five key business metrics:

- **Revenue:** Total sales generated.
- **Profit:** Total profit across transactions.
- **Profit Margin:** Profit divided by revenue, expressed as a percentage.
- **Orders:** Number of distinct orders.
- **Units Sold:** Total quantity sold.

### 2. Interactive Filters

Users can explore supported analytics using:

- Date range
- Region
- Product category

### 3. Monthly Revenue Trend

Visualizes historical revenue across months to help identify changes and patterns in sales performance.

### 4. Month-over-Month Growth

Compares monthly revenue against the previous month to show percentage growth or decline.

### 5. Regional Performance

Compares revenue and profit margins across different regions.

### 6. Category Performance

Analyzes revenue generated by different product categories.

### 7. Product Performance

Displays top-performing products and product-level details to help identify important contributors to sales.

## 🤖 Sales Forecasting

The platform includes a monthly revenue forecasting feature built using **Random Forest Regression** from Scikit-learn.

### Model Configuration

```python
RandomForestRegressor(
    n_estimators=300,
    max_depth=5,
    min_samples_leaf=2,
    random_state=42
)
```

### Features Used

| Feature | Description |
|---|---|
| `Month_Number` | Calendar month |
| `Year` | Calendar year |
| `Time_Index` | Sequential monthly index |
| `Lag_1` | Previous month's revenue |
| `Lag_2` | Revenue from two months earlier |
| `Lag_3` | Revenue from three months earlier |
| `Rolling_Mean_3` | Rolling average of recent monthly revenue |

### Model Evaluation

The recorded evaluation results on the final six months of the historical series were:

| Evaluation Metric | Value |
|---|---:|
| MAE | $17,692.73 |
| RMSE | $21,428.33 |
| MAPE | 20.91% |

### Example Forecast Results

An earlier model run produced these estimates:

| Month | Forecast Revenue |
|---|---:|
| January 2018 | $46,099.69 |
| February 2018 | $46,766.55 |
| March 2018 | $51,568.94 |

> **Note:** These are recorded development results, not guaranteed future predictions. The historical dataset is relatively short, so forecasts should be treated as exploratory estimates rather than financial guidance.

## 💬 Rule-Based Chatbot

The application includes a simple **rule-based sales chatbot** that identifies supported question patterns and executes predefined, read-only SQL queries against sales data.

The chatbot does not require an LLM API.

### Supported Questions

- Total revenue or sales.
- Total profit.
- Highest-profit region.
- Lowest-profit region.
- Products with negative profit.
- Category performance.
- Revenue by region.
- Help and supported-question guidance.

The chatbot is limited to the intents implemented in the application. It is not a general-purpose AI assistant and does not generate arbitrary SQL queries.

## 📁 Project Structure

```text
Salesdatabricks/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

| File | Description |
|---|---|
| `app.py` | Streamlit dashboard, analytics, forecasting, and chatbot |
| `.env` | Local Databricks connection settings |
| `.gitignore` | Excludes secrets and local environment files |
| `requirements.txt` | Python package dependencies |
| `README.md` | Project documentation |

Databricks notebooks or SQL scripts used to create the data layers can also be included in the repository.

## ⚙️ Installation and Setup

### Prerequisites

Ensure you have:

- Python installed.
- A Databricks workspace.
- A running Databricks SQL Warehouse.
- Access to the required catalog, schema, volume, and tables.
- A valid Databricks authentication token or another supported authentication method.
- The Superstore CSV uploaded to Databricks.
- The Bronze, Silver, and Gold tables created.

### Step 1: Clone the Repository

Replace the placeholder with your actual repository URL.

```bash
git clone <YOUR_REPOSITORY_URL>
cd Salesdatabricks
```

If the project already exists locally, open a terminal in the project directory.

### Step 2: Create a Virtual Environment

On Windows PowerShell:

```powershell
py -m venv sales
.\sales\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Create a `requirements.txt` file containing:

```text
streamlit
databricks-sql-connector
python-dotenv
pandas
plotly
scikit-learn
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Add any additional packages imported by your application.

## 🔐 Environment Variables

Create a `.env` file in the project root.

```dotenv
DATABRICKS_SERVER_HOSTNAME=your-workspace-hostname
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_TOKEN=your-access-token
```

Replace the example values with your own Databricks connection details.

Load the environment variables in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()

server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
http_path = os.getenv("DATABRICKS_HTTP_PATH")
access_token = os.getenv("DATABRICKS_TOKEN")
```

**Security warning:** Never commit your real access token or `.env` file to a public repository.

## ▶️ Running the Application

After configuring the environment and installing dependencies, run:

```powershell
python -m streamlit run app.py
```

Streamlit will display a local URL, usually:

```text
http://localhost:8501
```

Open the URL in your browser to access the Retail Sales Intelligence Platform.

## 💡 Example Chatbot Questions

Try the following questions in the dashboard chatbot:

- What is the total revenue?
- What is the total profit?
- Which region has the highest profit?
- Which region has the lowest profit?
- Show products with negative profit.
- How are the categories performing?
- What is the revenue by region?
- What questions can I ask?

The precise wording accepted depends on the intent patterns implemented in `app.py`.

## 🛠️ Troubleshooting

### Databricks Authentication Errors

- Verify that the token is valid and has not expired.
- Check the server hostname and HTTP path.
- Ensure the SQL Warehouse is running.
- Verify permissions to use the warehouse and query the required tables.
- Confirm the `.env` file is in the correct directory.

### Table or Schema Not Found

- Verify the catalog, schema, and table names.
- Confirm that the required tables have been created.
- Check the permissions of the application identity.

### CSV Encoding Errors

If the CSV contains Windows-encoded characters, try an appropriate encoding such as `cp1252` when reading it with Pandas.

### Delta Lake Column Errors

Normalize column names before writing Delta tables if they contain unsupported spaces or special characters.

### Date or Numeric Casting Errors

Inspect invalid values before converting dates and numerical columns. Use explicit parsing and appropriate data types during the Silver transformation.

### Streamlit Fails to Start

- Activate the virtual environment.
- Install missing dependencies.
- Run the command from the directory containing `app.py`.
- Review the first traceback in the terminal.

### Dashboard Data Does Not Refresh

- Use the dashboard refresh control if available.
- Review Streamlit cache settings.
- Verify that the SQL queries are reading the intended Databricks tables.

## 🔒 Security

- Never commit `.env` or access tokens.
- Revoke and replace any token that has been exposed.
- Prefer read-only permissions for dashboard queries.
- Avoid logging credentials or sensitive connection information.
- Grant the application only the Databricks permissions it requires.

Recommended `.gitignore` entries:

```gitignore
.env
sales/
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
```

## 🚀 Future Enhancements

- Add automated data-quality checks and pipeline validation.
- Orchestrate the Bronze-to-Silver-to-Gold pipeline.
- Add more detailed analytics by state, segment, customer, and sub-category.
- Improve forecasting with time-series cross-validation and seasonal baselines.
- Compare Random Forest against alternative forecasting models.
- Add prediction ranges where appropriate.
- Expand chatbot intents and improve fallback responses.
- Add automated tests for SQL transformations, metrics, and forecasts.
- Deploy the dashboard using secure secret management.
- Add dashboard screenshots or a demo GIF to the repository.

## 📌 Disclaimer

This project is intended for learning and demonstration. Dashboard metrics and forecasts depend on the source data and implementation. Validate business-critical results independently before using them for operational or financial decisions.

---

**Built with:** Python | Databricks | PySpark | Delta Lake | Streamlit | Scikit-learn
