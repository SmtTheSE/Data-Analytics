import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load preprocessed data
df = pd.read_csv('data/transactions_with_revenue_userinfo.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M').astype(str)

# Print columns for debug
print("Columns in df:", df.columns.tolist())

# Column name handling for merchant name
merchant_col = None
for name in ['Merchant_name', 'merchant_name', 'Merchant', 'merchant']:
    if name in df.columns:
        merchant_col = name
        break

if merchant_col is None:
    print(" Merchant name column not found. Merchant revenue chart will be skipped.")

# Aggregate data for visuals
monthly_revenue = df.groupby('Month')['Revenue'].sum().reset_index()
monthly_transactions = df.groupby('Month')['user_id'].count().reset_index(name='Transactions')
monthly_active_users = df.groupby('Month')['user_id'].nunique().reset_index(name='Active Users')
monthly_new_users = df[df['Type_user'] == 'New'].groupby('Month')['user_id'].nunique().reset_index(name='New Users')

app = Dash(__name__)

app.layout = html.Div([
    html.H1("MoMo Service Performance Dashboard"),

    dcc.Dropdown(
        id='metric-dropdown',
        options=[
            {'label': 'Monthly Revenue', 'value': 'Revenue'},
            {'label': 'Number of Transactions', 'value': 'Transactions'},
            {'label': 'Active Users', 'value': 'Active Users'},
            {'label': 'New Users', 'value': 'New Users'}
        ],
        value='Revenue'
    ),
    dcc.Graph(id='main-metric-graph'),

    html.H2("Revenue by Merchant"),
    dcc.Graph(
        id='merchant-graph',
        figure=(
            px.bar(
                df.groupby(['Month', merchant_col])['Revenue'].sum().reset_index(),
                x='Month', y='Revenue', color=merchant_col, barmode='group',
                title='Monthly Revenue by Merchant'
            ) if merchant_col else {}
        )
    ),

    html.H2("Revenue by Age Group"),
    dcc.Graph(
        figure=px.bar(
            df.groupby(['Month', 'Age'])['Revenue'].sum().reset_index(),
            x='Month', y='Revenue', color='Age', barmode='group',
            title='Monthly Revenue by Age Group'
        )
    ),

    html.H2("Revenue by Day of Week (All Time)"),
    dcc.Graph(
        figure=px.bar(
            df.groupby(df['Date'].dt.day_name())['Revenue'].mean().reset_index(),
            x='Date', y='Revenue',
            title='Average Revenue by Weekday'
        )
    ),
])

@app.callback(
    Output('main-metric-graph', 'figure'),
    [Input('metric-dropdown', 'value')]
)
def update_main_metric(metric):
    if metric == 'Revenue':
        fig = px.bar(monthly_revenue, x='Month', y='Revenue', title='Monthly Revenue')
    elif metric == 'Transactions':
        fig = px.bar(monthly_transactions, x='Month', y='Transactions', title='Monthly Transactions')
    elif metric == 'Active Users':
        fig = px.bar(monthly_active_users, x='Month', y='Active Users', title='Monthly Active Users')
    elif metric == 'New Users':
        fig = px.bar(monthly_new_users, x='Month', y='New Users', title='Monthly New Users')
    else:
        fig = {}
    return fig

if __name__ == '__main__':
    app.run(debug=True)