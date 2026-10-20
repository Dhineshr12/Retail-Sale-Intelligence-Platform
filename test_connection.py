import pandas as pd

df = pd.read_csv("Superstore.csv", encoding="cp1252")


# 1. Display first 5 rows
print("First 5 rows:")
print(df.head())

# 2. Check dataset dimensions
print("\nDataset shape:")
print(df.shape)

# 3. Display column names
print("\nColumn names:")
print(df.columns.tolist())

# 4. Check data types and missing values
print("\nDataset information:")
df.info()

# 5. Count missing values
print("\nMissing values:")
print(df.isnull().sum())

# 6. Check duplicate rows
print("\nDuplicate rows:", df.duplicated().sum())

# 7. Get statistical summary
print("\nStatistical summary:")
print(df.describe(include="all"))
auth_type="databricks-oauth"

