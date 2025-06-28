import pandas as pd

# ----------- STEP 1: Load Data -----------
transactions = pd.read_csv('data/transactions_final.csv')
commission = pd.read_csv('data/commission_final.csv')
user_info = pd.read_csv('data/user_info_final.csv')

print("\n--- Loaded files ---")
print(f"transactions: {transactions.shape}")
print(f"commission: {commission.shape}")
print(f"user_info: {user_info.shape}")

# Remove duplicates on keys
commission = commission.drop_duplicates(subset=['Merchant_id'])
user_info = user_info.drop_duplicates(subset=['User_id'])

# Ensure numeric columns
transactions['Amount'] = pd.to_numeric(transactions['Amount'], errors='coerce')
commission['Rate_pct'] = pd.to_numeric(commission['Rate_pct'], errors='coerce')

# Merge commission into transactions
merged = pd.merge(
    transactions,
    commission[['Merchant_id', 'Rate_pct', 'Merchant_name']],
    how='left',
    left_on='Merchant_id',
    right_on='Merchant_id'
)

print(f"\n--- After merge: merged shape = {merged.shape} ---")
print("Sample merged rows:")
print(merged.head(3))

# ----------- STEP 2: Add Revenue column -----------
merged['Revenue'] = merged['Amount'] * (merged['Rate_pct'] / 100)

# Check for missing or NaN values in key columns
print("\nMissing values after merge:")
print(merged[['Amount', 'Rate_pct', 'Revenue']].isnull().sum())

# Parse dates
merged['Date'] = pd.to_datetime(merged['Date'], errors='coerce')

# Check for parsing errors in Date
print("\nDate parsing check:")
print(merged['Date'].isnull().sum(), "rows have invalid Date after parsing.")

# ----------- Q1: MoMo's total revenue in January 2020 -----------
jan2020 = merged[merged['Date'].dt.to_period('M') == pd.Period('2020-01')]

print("\n--- January 2020 rows ---")
print("Number of rows in Jan 2020:", len(jan2020))
print("Sample Jan 2020 rows:")
print(jan2020[['Date', 'Amount', 'Rate_pct', 'Revenue']].head(10))

# Check for missing Revenue in Jan 2020
print("Missing Revenue in Jan 2020:", jan2020['Revenue'].isnull().sum())

# Check for possible duplicate orders
jan2020_duplicates = jan2020.duplicated(subset=['order_id'])
print("Duplicate order_ids in Jan 2020:", jan2020_duplicates.sum())

total_revenue_jan2020 = jan2020['Revenue'].sum(min_count=1)
print(f"\n1. MoMo's total revenue in January 2020: {total_revenue_jan2020:,.0f} VND")

# ----------- Q2: Most profitable month -----------
merged['Month'] = merged['Date'].dt.to_period('M')
revenue_by_month = merged.groupby('Month')['Revenue'].sum()
most_profitable_month = revenue_by_month.idxmax()
most_profitable_month_value = revenue_by_month.max()
print(f"\n2. Most profitable month: {most_profitable_month} (Revenue: {most_profitable_month_value:,.0f} VND)")

# ----------- Q3: Day of week with most/least average revenue -----------
merged['weekday'] = merged['Date'].dt.day_name()
avg_revenue_by_weekday = merged.groupby('weekday')['Revenue'].mean()
# Order weekdays for display
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
avg_revenue_by_weekday = avg_revenue_by_weekday.reindex(weekday_order)
most_profitable_day = avg_revenue_by_weekday.idxmax()
least_profitable_day = avg_revenue_by_weekday.idxmin()
print("\n3. Average revenue by weekday:")
print(avg_revenue_by_weekday)
print(f"   Most profitable day: {most_profitable_day} ({avg_revenue_by_weekday.max():,.0f} VND)")
print(f"   Least profitable day: {least_profitable_day} ({avg_revenue_by_weekday.min():,.0f} VND)")

# ----------- Q4: Add user info & calculate new users in Dec 2020 -----------
# Merge user info
merged = pd.merge(
    merged,
    user_info[['User_id', 'Age', 'Gender', 'Location', 'First_tran_date']],
    how='left',
    left_on='user_id',
    right_on='User_id'
)

# Add Type_user column
merged['First_tran_date'] = pd.to_datetime(merged['First_tran_date'], errors='coerce')
merged['tran_month'] = merged['Date'].dt.to_period('M')
merged['first_tran_month'] = merged['First_tran_date'].dt.to_period('M')
merged['Type_user'] = merged.apply(lambda row:
                                   'New' if row['tran_month'] == row['first_tran_month'] else 'Current',
                                   axis=1)

# Calculate total number of new users in Dec 2020
dec2020_new_users = merged[
    (merged['tran_month'] == pd.Period('2020-12')) &
    (merged['Type_user'] == 'New')
]['user_id'].nunique()
print(f"\n4. Total number of new users in December 2020: {dec2020_new_users}")

# Save the fully processed transactions for reference
merged.to_csv('data/transactions_with_revenue_userinfo.csv', index=False)
print("\nDetailed transactions with revenue and user info saved as data/transactions_with_revenue_userinfo.csv")


summary_data = {
    "Question": [
        "MoMo's total revenue in January 2020",
        "Most profitable month",
        "Most profitable weekday (average revenue)",
        "Least profitable weekday (average revenue)",
        "Total number of new users in December 2020"
    ],
    "Answer": [
        f"{total_revenue_jan2020:,.0f} VND",
        f"{most_profitable_month} (Revenue: {most_profitable_month_value:,.0f} VND)",
        f"{most_profitable_day} ({avg_revenue_by_weekday.max():,.0f} VND)",
        f"{least_profitable_day} ({avg_revenue_by_weekday.min():,.0f} VND)",
        dec2020_new_users
    ]
}

# Convert to DataFrame and export
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv("data/summary_results.csv", index=False, encoding='utf-8-sig')

print("\n📄 Summary results saved as: data/summary_results.csv")
