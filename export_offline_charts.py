import pandas as pd
import xlsxwriter

# Reload or reuse df if already defined
df = pd.read_csv('data/transactions_with_revenue_userinfo.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').astype(str)

# Prepare summaries
monthly_revenue = df.groupby('Month')['Revenue'].sum().reset_index()
monthly_transactions = df.groupby('Month')['user_id'].count().reset_index(name='Transactions')
monthly_active_users = df.groupby('Month')['user_id'].nunique().reset_index(name='Active Users')
monthly_new_users = df[df['Type_user'] == 'New'].groupby('Month')['user_id'].nunique().reset_index(name='New Users')
weekday_revenue = df.groupby(df['Date'].dt.day_name())['Revenue'].mean().reset_index()
weekday_revenue = weekday_revenue.rename(columns={'Date': 'Weekday'}).sort_values(by='Revenue', ascending=False)

# Identify merchant column
merchant_col = None
for col in ['Merchant_name', 'merchant_name', 'Merchant', 'merchant']:
    if col in df.columns:
        merchant_col = col
        break

merchant_revenue = (
    df.groupby(['Month', merchant_col])['Revenue'].sum().reset_index()
    if merchant_col else pd.DataFrame()
)

age_revenue = df.groupby(['Month', 'Age'])['Revenue'].sum().reset_index()



# Excel export path
output_path = 'data/hackathon_dashboard_output.xlsx'

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    # Write data
    monthly_revenue.to_excel(writer, sheet_name='Monthly Revenue', index=False)
    monthly_transactions.to_excel(writer, sheet_name='Transactions', index=False)
    monthly_active_users.to_excel(writer, sheet_name='Active Users', index=False)
    monthly_new_users.to_excel(writer, sheet_name='New Users', index=False)
    weekday_revenue.to_excel(writer, sheet_name='Weekday Revenue', index=False)
    if not merchant_revenue.empty:
        merchant_revenue.to_excel(writer, sheet_name='Merchant Revenue', index=False)
    age_revenue.to_excel(writer, sheet_name='Age Revenue', index=False)

    workbook = writer.book

    # Helper to insert column chart in any sheet
    def insert_chart(sheet_name, label_col, value_col, chart_title, x_axis_name, y_axis_name):
        worksheet = writer.sheets[sheet_name]
        data_len = worksheet.dim_rowmax  # Number of rows in data
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': [sheet_name, 0, value_col],
            'categories': [sheet_name, 1, label_col, data_len, label_col],
            'values': [sheet_name, 1, value_col, data_len, value_col],
        })
        chart.set_title({'name': chart_title})
        chart.set_x_axis({'name': x_axis_name})
        chart.set_y_axis({'name': y_axis_name})
        worksheet.insert_chart('E2', chart)

    # Insert charts for each basic sheet
    insert_chart('Monthly Revenue', 0, 1, 'Monthly Revenue', 'Month', 'Revenue (VND)')
    insert_chart('Transactions', 0, 1, 'Monthly Transactions', 'Month', 'Number of Transactions')
    insert_chart('Active Users', 0, 1, 'Monthly Active Users', 'Month', 'Active Users')
    insert_chart('New Users', 0, 1, 'Monthly New Users', 'Month', 'New Users')
    insert_chart('Weekday Revenue', 0, 1, 'Avg Revenue by Weekday', 'Day', 'Revenue (VND)')


    # Optional: add charts for multi-category sheets
    if not merchant_revenue.empty:
        worksheet = writer.sheets['Merchant Revenue']
        worksheet.write('E1', 'Tip: Pivot this in Excel for stacked view')

    worksheet = writer.sheets['Age Revenue']
    worksheet.write('E1', 'Tip: Use Excel PivotChart for Age breakdown')


print(f" Excel dashboard exported to {output_path}")
