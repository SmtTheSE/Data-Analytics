import pandas as pd

transactions = pd.read_csv('data/transactions_final.csv')
commission = pd.read_csv('data/commission_final.csv')
user_info = pd.read_csv('data/user_info_final.csv')

# Remove duplicates on merge keys
commission = commission.drop_duplicates(subset=['Merchant_id'])
user_info = user_info.drop_duplicates(subset=['User_id'])

# --- UPDATE THIS MERGE TO INCLUDE Merchant_name ---
merged = pd.merge(
    transactions,
    commission[['Merchant_id', 'Rate_pct', 'Merchant_name']],  # <-- add 'Merchant_name'
    how='left',
    left_on='Merchant_id',
    right_on='Merchant_id'
)

# Debug: Check uniqueness
if user_info['User_id'].duplicated().any():
    dupes = user_info[user_info['User_id'].duplicated(keep=False)]
    print("Duplicate User_id in user_info:", dupes)
    raise ValueError("Duplicates found in User_id after drop_duplicates!")

if commission['Merchant_id'].duplicated().any():
    dupes = commission[commission['Merchant_id'].duplicated(keep=False)]
    print("Duplicate Merchant_id in commission:", dupes)
    raise ValueError("Duplicates found in Merchant_id after drop_duplicates!")

# Merge Transactions with Commission
merged = pd.merge(
    transactions,
    commission,
    how='left',
    left_on='Merchant_id',
    right_on='Merchant_id',
    validate='many_to_one'
)

# Merge with User_Info
merged = pd.merge(
    merged,
    user_info,
    how='left',
    left_on='user_id',
    right_on='User_id',
    validate='many_to_one'
)

if 'User_id' in merged.columns:
    merged = merged.drop(columns=['User_id'])

merged.to_csv('data/master_merged.csv', index=False)
print(" Master merged dataset saved as data/master_merged.csv")