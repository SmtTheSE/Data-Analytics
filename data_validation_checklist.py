import pandas as pd

# Load cleaned data
transactions = pd.read_csv('data/transactions_cleaned.csv')
user_info = pd.read_csv('data/user_info_cleaned.csv')
commission = pd.read_csv('data/commission_cleaned.csv')

print("\n========== VALIDATION CHECK: TRANSACTIONS ==========\n")
print(transactions.info())
print(transactions.describe(include='all'))

for col in transactions.select_dtypes(include='datetime').columns:
    print(f"{col} min: {transactions[col].min()}, max: {transactions[col].max()}")
print("Sample rows:\n", transactions.head())

print("Nulls per column:\n", transactions.isnull().sum())
print("Any negative or zero amounts?", (transactions['amount'] <= 0).sum())
print("Unique purchase_status:", transactions['purchase_status'].unique() if 'purchase_status' in transactions.columns else "N/A")
print("Outlier amounts (99.9th percentile):", transactions['amount'].quantile(0.999))

# Check for invalid dates (future or NaT)
if 'date' in transactions.columns:
    print("Any future dates?", (pd.to_datetime(transactions['date'], errors='coerce') > pd.Timestamp.today()).sum())
    print("Any invalid dates?", pd.to_datetime(transactions['date'], errors='coerce').isnull().sum())

# User IDs in transactions vs user_info
print("\n========== VALIDATION CHECK: USERS ==========\n")
print(user_info.info())
print(user_info.describe(include='all'))
print("Sample rows:\n", user_info.head())
print("Nulls per column:\n", user_info.isnull().sum())
print("User IDs in transactions not in user_info:", set(transactions['user_id']) - set(user_info['user_id']))

# Merchant IDs in transactions vs commission
print("\n========== VALIDATION CHECK: COMMISSION ==========\n")
print(commission.info())
print(commission.describe(include='all'))
print("Sample rows:\n", commission.head())
print("Nulls per column:\n", commission.isnull().sum())
print("Merchant IDs in transactions not in commission:", set(transactions['merchant_id']) - set(commission['merchant_id']))

# Categorical sanity checks
print("\n========== VALIDATION CHECK: CATEGORICALS ==========\n")
if 'gender' in user_info.columns:
    print("Gender values:", user_info['gender'].unique())
if 'location' in user_info.columns:
    print("Location sample:", user_info['location'].unique()[:10])

# Logical checks -- FIXED: use merge to avoid length mismatch
if 'first_tran_date' in user_info.columns and 'date' in transactions.columns:
    transactions['date'] = pd.to_datetime(transactions['date'], errors='coerce')
    user_info['first_tran_date'] = pd.to_datetime(user_info['first_tran_date'], errors='coerce')
    merged = pd.merge(
        transactions[['user_id', 'date']],
        user_info[['user_id', 'first_tran_date']],
        on='user_id', how='left'
    )
    invalid = (merged['date'] < merged['first_tran_date']).sum()
    print(f"Transactions before user's first transaction date: {invalid}")

print("\n========== VALIDATION CHECK COMPLETE ==========\n")