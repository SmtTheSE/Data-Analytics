import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. Load Data ---
file_path = 'mini-Hackathon-question.xlsx'
transactions = pd.read_excel(file_path, sheet_name='Data Transactions')
commission = pd.read_excel(file_path, sheet_name='Data Commission')
user_info = pd.read_excel(file_path, sheet_name='Data User_Info')

# --- 2. Standardize Column Names ---
def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

transactions = clean_columns(transactions)
commission = clean_columns(commission)
user_info = clean_columns(user_info)

print("\nLoaded, initial transactions shape:", transactions.shape)
print("First few rows:\n", transactions.head())

# --- 3. Clean and Convert 'amount' to Numeric ---
if 'amount' in transactions.columns:
    transactions['amount'] = (
        transactions['amount']
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.strip()
    )
    transactions['amount'] = pd.to_numeric(transactions['amount'], errors='coerce')
    print("\nAfter amount to_numeric, nulls:", transactions['amount'].isna().sum())

# --- 4. Convert 'date' to datetime ---
if 'date' in transactions.columns:
    transactions['date'] = pd.to_datetime(transactions['date'], errors='coerce')
    print("After date to_datetime, nulls:", transactions['date'].isna().sum())

# --- 5. Remove Duplicates ---
transactions = transactions.drop_duplicates()
commission = commission.drop_duplicates()
user_info = user_info.drop_duplicates()
print("\nAfter dropping duplicates, transactions shape:", transactions.shape)

# --- 6. Basic Null Diagnostics ---
print("\nNull counts BEFORE dropping rows:")
print(transactions.isnull().sum())

# --- 7. Drop Rows with Missing Truly Critical Fields ---
must_have = ['user_id', 'order_id', 'date', 'amount']
transactions = transactions.dropna(subset=[col for col in must_have if col in transactions.columns])
print("\nAfter dropping rows with missing critical fields, shape:", transactions.shape)

# --- 8. Remove Zero/Negative Amounts ---
if 'amount' in transactions.columns:
    before = transactions.shape[0]
    transactions = transactions[transactions['amount'] > 0]
    print(f"Removed {before - transactions.shape[0]} rows with amount <= 0")

# --- 9. Categorical Harmonization ---
# Gender
if 'gender' in user_info.columns:
    user_info['gender'] = user_info['gender'].replace({
        'male': 'Male', 'MALE': 'Male', 'M': 'Male', 'male_': 'Male',
        'female': 'Female', 'FEMALE': 'Female', 'F': 'Female', 'female_': 'Female',
        'unknown': 'Unknown', '': 'Unknown', np.nan: 'Unknown'
    })
# Location
if 'location' in user_info.columns:
    user_info['location'] = user_info['location'].replace({
        'Ho Chi Minh City': 'HCMC', 'Other Cities': 'Other', '': 'Unknown', np.nan: 'Unknown'
    })
    user_info['location'] = user_info['location'].fillna('Unknown')

# Age (optional: harmonize 'unknown')
if 'age' in user_info.columns:
    user_info['age'] = user_info['age'].replace({'': 'Unknown', np.nan: 'Unknown'})

# --- 10. Commission Data Types ---
if 'rate_pct' in commission.columns:
    commission['rate_pct'] = pd.to_numeric(commission['rate_pct'], errors='coerce')

# --- 11. Feature Engineering ---
if 'date' in transactions.columns:
    transactions['month'] = transactions['date'].dt.month
    transactions['year'] = transactions['date'].dt.year
    transactions['week'] = transactions['date'].dt.isocalendar().week
    transactions['weekday'] = transactions['date'].dt.day_name()

# --- 12. Merge First Transaction Date, User Type, Tenure ---
if 'first_tran_date' in user_info.columns:
    user_info['first_tran_date'] = pd.to_datetime(user_info['first_tran_date'], errors='coerce')
if 'user_id' in transactions.columns and 'first_tran_date' in user_info.columns:
    transactions = transactions.merge(
        user_info[['user_id', 'first_tran_date']], on='user_id', how='left'
    )
    transactions['tenure_days'] = (transactions['date'] - transactions['first_tran_date']).dt.days
    transactions['first_tran_month'] = transactions['first_tran_date'].dt.to_period('M')
    transactions['tran_month'] = transactions['date'].dt.to_period('M')
    transactions['type_user'] = np.where(
        transactions['first_tran_month'] == transactions['tran_month'], 'New', 'Current'
    )

# --- 13. Transactions per User ---
if 'user_id' in transactions.columns and 'order_id' in transactions.columns:
    user_tx_count = transactions.groupby('user_id')['order_id'].count().rename('total_tx')
    transactions = transactions.merge(user_tx_count, on='user_id', how='left')

# --- 14. Commission Mapping  ---
if 'merchant_id' in transactions.columns and 'merchant_id' in commission.columns:
    transactions = transactions.merge(
        commission[['merchant_id', 'rate_pct']],
        on='merchant_id', how='left'
    )
    if 'rate_pct' in transactions.columns:
        transactions['revenue'] = transactions['amount'] * transactions['rate_pct'] / 100

# --- 15. Data Dictionary Output ---
def data_dictionary(df, name):
    print(f"\nData Dictionary for {name}:")
    for col in df.columns:
        print(f"{col}: {df[col].dtype}, unique: {df[col].nunique()}, sample: {df[col].unique()[:5]}")

print("\nFinal transactions shape:", transactions.shape)
data_dictionary(transactions, 'transactions')
data_dictionary(user_info, 'user_info')
data_dictionary(commission, 'commission')

# --- 16. Ensure 'data' directory exists before saving ---
os.makedirs('data', exist_ok=True)

# --- 17. Save Cleaned Data ---
transactions.to_csv('data/transactions_cleaned.csv', index=False)
commission.to_csv('data/commission_cleaned.csv', index=False)
user_info.to_csv('data/user_info_cleaned.csv', index=False)
print("\n Cleaned data saved to 'data/'")

# --- 18. Visual Data Audit - Save Plots (only if data exists) ---
if 'amount' in transactions.columns and not transactions['amount'].dropna().empty:
    plt.figure(figsize=(8,4))
    transactions['amount'].hist(bins=50)
    plt.title('Transaction Amount Distribution')
    plt.xlabel('Amount (VND)')
    plt.ylabel('Count')
    plt.savefig('data/amount_hist.png')
    plt.close()
    print("Saved amount histogram.")
else:
    print("No data to plot for 'amount' distribution.")

if 'weekday' in transactions.columns and not transactions['weekday'].dropna().empty:
    weekday_counts = transactions['weekday'].value_counts().sort_index()
    if not weekday_counts.empty:
        plt.figure(figsize=(8,4))
        weekday_counts.plot(kind='bar')
        plt.title('Transactions by Weekday')
        plt.xlabel('Weekday')
        plt.ylabel('Number of Transactions')
        plt.savefig('data/weekday_bar.png')
        plt.close()
        print("Saved weekday bar plot.")
    else:
        print("No transactions by weekday to plot.")
else:
    print("No data to plot for 'weekday' bar chart.")

print("\n Data cleaning and feature engineering completed successfully!")