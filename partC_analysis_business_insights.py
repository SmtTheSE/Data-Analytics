import pandas as pd

# Load merged and enriched transaction data
df = pd.read_csv('data/transactions_with_revenue_userinfo.csv')
df['Date'] = pd.to_datetime(df['Date'])

# ------------- Q6: User demographics & transaction behavior -------------
print("\nQ6: User Demographics & Transaction Behavior\n")

# Demographic breakdowns
print("User count by Age group:")
print(df.groupby('Age')['user_id'].nunique())

print("\nUser count by Gender:")
print(df.groupby('Gender')['user_id'].nunique())

print("\nUser count by Location:")
print(df.groupby('Location')['user_id'].nunique())

# Transactional trends
print("\nTransaction count by Age group:")
print(df.groupby('Age')['order_id'].count())

print("\nTransaction count by Gender:")
print(df.groupby('Gender')['order_id'].count())

print("\nTransaction count by Location:")
print(df.groupby('Location')['order_id'].count())

print("\nAverage transaction value by Age group:")
print(df.groupby('Age')['Amount'].mean())

print("\nAverage transaction value by Gender:")
print(df.groupby('Gender')['Amount'].mean())

print("\nAverage transaction value by Location:")
print(df.groupby('Location')['Amount'].mean())

print("\nMonthly trend: Transactions and revenue per month:")
monthly = df.groupby(df['Date'].dt.to_period('M')).agg(
    Transactions=('order_id', 'count'),
    Revenue=('Revenue', 'sum'),
    New_Users=('user_id', lambda x: (df.loc[x.index, 'Type_user'] == 'New').sum())
)
print(monthly)

# ------------- Q7: Marketing advice metrics -------------
print("\nQ7: Marketing Advice Metrics\n")

# Most valuable user segments
revenue_by_age = df.groupby('Age')['Revenue'].sum()
revenue_by_gender = df.groupby('Gender')['Revenue'].sum()
revenue_by_location = df.groupby('Location')['Revenue'].sum()

print("Revenue by Age group:\n", revenue_by_age)
print("\nRevenue by Gender:\n", revenue_by_gender)
print("\nRevenue by Location:\n", revenue_by_location)

# Frequency: top users
user_freq = df.groupby('user_id')['order_id'].count().sort_values(ascending=False)
print("\nTop 5 most active users (by transaction count):")
print(user_freq.head())

# ------------- Q8: Cashback proposal impact -------------

print("\nQ8: Cashback Proposal Impact\n")

# List of Telco merchants (as per cashback table)
telco_merchants = {
    'Viettel': 2,
    'Mobifone': 2.5,
    'Vinaphone': 3,
    'Vietnamobile': 3,
    'Gmobile': 3
}
if 'Merchant_name' not in df.columns:
    # Add mapping from Merchant_id to name
    merchant_id_map = {
        12: 'Viettel',
        13: 'Mobifone',
        14: 'Vinaphone',
        15: 'Vietnamobile',
        16: 'Gmobile'
    }
    df['Merchant_name'] = df['Merchant_id'].map(merchant_id_map)

# Mark telco transactions
df['Is_telco'] = df['Merchant_name'].isin(telco_merchants.keys())

# Current cashback (1% for all telco)
df['Current_cashback'] = df.apply(
    lambda row: 0.01 * row['Amount'] if row['Is_telco'] else 0, axis=1
)
# Proposed cashback (use table above)
df['Proposed_cashback'] = df.apply(
    lambda row: (telco_merchants[row['Merchant_name']] / 100) * row['Amount'] if row['Is_telco'] else 0, axis=1
)

# Compute costs
current_cashback_total = df['Current_cashback'].sum()
proposed_cashback_total = df['Proposed_cashback'].sum()
additional_cost = proposed_cashback_total - current_cashback_total

print(f"Current total cashback paid: {current_cashback_total:,.0f} VND")
print(f"Proposed total cashback paid: {proposed_cashback_total:,.0f} VND")
print(f"Additional cost to MoMo: {additional_cost:,.0f} VND")

# Impact on revenue (for telco merchants)
telco_revenue = df[df['Is_telco']]['Revenue'].sum()
print(f"\nMoMo's revenue from Telco merchants: {telco_revenue:,.0f} VND")
print(f"Under proposal, % of revenue used for cashback: {proposed_cashback_total / telco_revenue * 100:.2f}%")

# ------------- Q9: User group ideas for development strategy -------------
print("\nQ9: User Group Breakdown for Strategy Ideas\n")

# Who are the top spenders?
spender = df.groupby('user_id')['Amount'].sum().sort_values(ascending=False)
print("Top 5 highest spenders (user_id):")
print(spender.head())

# Which user segments are less active? (could be targets for campaigns)
user_by_age = df.groupby('Age')['user_id'].nunique()
transactions_by_age = df.groupby('Age')['order_id'].count()
print("\nUser count by Age group:", user_by_age)
print("Transaction count by Age group:", transactions_by_age)


# ========== EXPORT PART C RESULTS TO EXCEL ==========
output_path = 'data/hackathon_partC_summary.xlsx'

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    # Q6: User Demographics & Behavior
    df.groupby('Age')['user_id'].nunique().reset_index(name='User Count').to_excel(writer, sheet_name='Q6_Age_UserCount', index=False)
    df.groupby('Gender')['user_id'].nunique().reset_index(name='User Count').to_excel(writer, sheet_name='Q6_Gender_UserCount', index=False)
    df.groupby('Location')['user_id'].nunique().reset_index(name='User Count').to_excel(writer, sheet_name='Q6_Location_UserCount', index=False)

    df.groupby('Age')['order_id'].count().reset_index(name='Transaction Count').to_excel(writer, sheet_name='Q6_Age_TransCount', index=False)
    df.groupby('Gender')['order_id'].count().reset_index(name='Transaction Count').to_excel(writer, sheet_name='Q6_Gender_TransCount', index=False)
    df.groupby('Location')['order_id'].count().reset_index(name='Transaction Count').to_excel(writer, sheet_name='Q6_Location_TransCount', index=False)

    df.groupby('Age')['Amount'].mean().reset_index(name='Avg Amount').to_excel(writer, sheet_name='Q6_Age_AvgAmt', index=False)
    df.groupby('Gender')['Amount'].mean().reset_index(name='Avg Amount').to_excel(writer, sheet_name='Q6_Gender_AvgAmt', index=False)
    df.groupby('Location')['Amount'].mean().reset_index(name='Avg Amount').to_excel(writer, sheet_name='Q6_Location_AvgAmt', index=False)

    monthly.to_timestamp().reset_index().to_excel(writer, sheet_name='Q6_Monthly_Trend', index=False)

    # Q7: Marketing Advice Metrics
    revenue_by_age.reset_index(name='Revenue').to_excel(writer, sheet_name='Q7_Revenue_By_Age', index=False)
    revenue_by_gender.reset_index(name='Revenue').to_excel(writer, sheet_name='Q7_Revenue_By_Gender', index=False)
    revenue_by_location.reset_index(name='Revenue').to_excel(writer, sheet_name='Q7_Revenue_By_Location', index=False)
    user_freq.head(5).reset_index(name='Transaction Count').to_excel(writer, sheet_name='Q7_Top_Users', index=False)

    # Q8: Cashback Proposal Impact
    cashback_df = pd.DataFrame({
        'Metric': [
            'Current Cashback Total',
            'Proposed Cashback Total',
            'Additional Cost',
            'Telco Revenue',
            'Cashback % of Telco Revenue'
        ],
        'Value (VND)': [
            round(current_cashback_total),
            round(proposed_cashback_total),
            round(additional_cost),
            round(telco_revenue),
            round(proposed_cashback_total / telco_revenue * 100, 2)
        ]
    })
    cashback_df.to_excel(writer, sheet_name='Q8_Cashback_Impact', index=False)

    # Q9: Strategy Segmentations
    spender.head(5).reset_index(name='Total Amount Spent').to_excel(writer, sheet_name='Q9_Top_Spenders', index=False)
    user_by_age.reset_index(name='User Count').to_excel(writer, sheet_name='Q9_Users_By_Age', index=False)
    transactions_by_age.reset_index(name='Transaction Count').to_excel(writer, sheet_name='Q9_Trans_By_Age', index=False)

print(f"\n Part C answers exported to: {output_path}")

