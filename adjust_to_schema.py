import pandas as pd
import numpy as np

# Load cleaned data (adjust paths as necessary)
transactions = pd.read_csv('data/transactions_cleaned.csv')
commission = pd.read_csv('data/commission_cleaned.csv')
user_info = pd.read_csv('data/user_info_cleaned.csv')


# 1. Transactions Sheet

# Rename columns to match schema exactly (case and underscores)
transactions = transactions.rename(columns={
    'user_id': 'user_id',
    'order_id': 'order_id',
    'date': 'Date',
    'amount': 'Amount',
    'merchant_id': 'Merchant_id',
    'purchase_status': 'Purchase_status'
})

# Keep only required columns, drop extras
transactions = transactions[['user_id', 'order_id', 'Date', 'Amount', 'Merchant_id', 'Purchase_status']]

# Data type adjustments
transactions['user_id'] = transactions['user_id'].astype(int)
transactions['order_id'] = transactions['order_id'].astype(int)
transactions['Date'] = pd.to_datetime(transactions['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
transactions['Amount'] = (
    transactions['Amount']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.strip()
)
transactions['Amount'] = pd.to_numeric(transactions['Amount'], errors='coerce').astype('Int64')
transactions['Merchant_id'] = transactions['Merchant_id'].astype(int)

# Standardize 'Purchase_status' values
transactions['Purchase_status'] = transactions['Purchase_status'].replace({
    'Purchase on behalf of someone': 'Mua hộ',
    'Mua ho': 'Mua hộ',
    'mua ho': 'Mua hộ',
    'mua hộ': 'Mua hộ',
    '': np.nan,
    np.nan: np.nan
})

# 2. Commission Sheet


commission = commission.rename(columns={
    'merchant_name': 'Merchant_name',
    'merchant_id': 'Merchant_id',
    'rate_pct': 'Rate_pct'
})
commission = commission[['Merchant_name', 'Merchant_id', 'Rate_pct']]
commission['Merchant_id'] = commission['Merchant_id'].astype(int)
commission['Rate_pct'] = pd.to_numeric(commission['Rate_pct'], errors='coerce').astype('Int64')

# 3. User_Info Sheet

user_info = user_info.rename(columns={
    'user_id': 'User_id',
    'first_tran_date': 'First_tran_date',
    'location': 'Location',
    'age': 'Age',
    'gender': 'Gender'
})
user_info = user_info[['User_id', 'First_tran_date', 'Location', 'Age', 'Gender']]

user_info['User_id'] = user_info['User_id'].astype(int)
user_info['First_tran_date'] = pd.to_datetime(user_info['First_tran_date'], errors='coerce').dt.strftime('%Y-%m-%d')

# Harmonize Gender (capitalize, map variants)
user_info['Gender'] = user_info['Gender'].replace({
    'male': 'Male', 'MALE': 'Male', 'M': 'Male', 'Male_': 'Male', 'male_': 'Male',
    'female': 'Female', 'FEMALE': 'Female', 'F': 'Female', 'female_': 'Female', 'FeMale_': 'Female',
    'f': 'Female', '': np.nan, np.nan: np.nan
})

#  Harmonize Location
user_info['Location'] = user_info['Location'].replace({
    'Ho Chi Minh City': 'HCMC', 'Other Cities': 'Other', '': np.nan, np.nan: np.nan
})


# 4. Save to Final Schema Files

transactions.to_csv('data/transactions_final.csv', index=False)
commission.to_csv('data/commission_final.csv', index=False)
user_info.to_csv('data/user_info_final.csv', index=False)
print(" All data adjusted and saved to 'data/*_final.csv' according to required schemas.")