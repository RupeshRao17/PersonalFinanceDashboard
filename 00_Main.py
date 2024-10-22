import pandas as pd
import numpy as np
import gspread
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Function to load data from Google Sheets
def load_data():
    # Authenticate with Google Sheets using service account
    ac = gspread.service_account(filename="personal_expenses.json")
    # Open the specific spreadsheet and worksheet
    gs = ac.open("personal_expenses")
    ws = gs.worksheet('Sheet1')
    # Get all records from the worksheet and convert to DataFrame
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    # Select relevant columns and rename for convenience
    df = df[['Completion_Date', 'Description', 'Amount']]
    df['Description'] = df['Description'].str.lower()  # Convert descriptions to lowercase
    df = df.rename(columns={'Completion_Date': 'Date'})
    return df

# Function to categorize expenses based on description
def categorize_expenses(df):
    # Default category for all rows
    df['Category'] = 'unassigned'
    # Apply categories based on keywords in the description
    df['Category'] = np.where(df['Description'].str.contains('store|fruit|food|vegetables|bakery|diary products'), 'Groceries', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('walmart|more|reliance smart|dmart|max|puma'), 'Shopping', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('barbeque|dominos|mcdonalds|restaurant|breakfast home'), 'Restaurants', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('coffee|soft drinks'), 'Drinks', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('cab|bus|train|flight'), 'Transport', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('movie|resort'), 'Entertainment', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('fuel'), 'Fuel', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('medicine|doctor'), 'HealthCare', df['Category'])
    df['Category'] = np.where(df['Description'].str.contains('self care'), 'SelfCare', df['Category'])
    return df

# Function to process data, including date conversion and month/year extraction
def process_data(df):
    df['Date'] = pd.to_datetime(df['Date'])  # Convert date column to datetime
    df['Month'] = df['Date'].dt.month  # Extract month from date
    df['Year'] = df['Date'].dt.year  # Extract year from date
    df['Month_Year'] = df['Date'].dt.strftime('%b %Y')  # Create Month-Year format
    df.to_csv('personal_expenses_sorted.csv', index=False)  # Save to CSV for reference
    return df

# Load, categorize, and process data
df = load_data()
df = categorize_expenses(df)
df = process_data(df)

# Function to create a pie chart based on selected category
def create_pie_chart(category):
    if category == 'Total':
        fig = px.pie(df, values='Amount', names='Category', title='Total Spending Breakdown')
    else:
        filtered_df = df[df['Category'] == category]
        fig = px.pie(filtered_df, values='Amount', names='Description', title=f'{category} Breakdown')
    
    fig.update_layout(
        plot_bgcolor='#2e2e36',  # Set background color
        paper_bgcolor='#2e2e36',  # Set paper color
        title={
            'text': f'{category} Breakdown' if category != 'Total' else 'Total Spending Breakdown',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white'}
        },
        title_font_color='white',
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0)'  # Transparent background for legend
        )
    )
    return fig

# Function to create a bar chart for monthly spending
def create_bar_chart(category):
    if category == 'Total':
        monthly_spending = df.groupby(['Year', 'Month_Year'])['Amount'].sum().reset_index()
    else:
        filtered_df = df[df['Category'] == category]
        monthly_spending = filtered_df.groupby(['Year', 'Month_Year'])['Amount'].sum().reset_index()

    monthly_spending['Month_Year_Sort'] = pd.to_datetime(monthly_spending['Month_Year'], format='%b %Y')
    monthly_spending = monthly_spending.sort_values('Month_Year_Sort')  # Sort by date

    fig = px.bar(
        monthly_spending,
        x='Month_Year',
        y='Amount',
        title='Monthly Spending Overview',
        color_discrete_sequence=['#5e5e5e']  # Set bar color
    )

    fig.update_layout(
        plot_bgcolor='#2e2e36',
        paper_bgcolor='#2e2e36',
        title={
            'text': 'Monthly Spending Overview',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white'}
        },
        title_font_color='white',
        xaxis=dict(
            title='Month',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title='Amount',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    return fig

# Function to create a scatter plot for spending
def create_scatter_plot(category):
    filtered_df = df[df['Category'] == category] if category != 'Total' else df
    fig = px.scatter(
        filtered_df,
        x='Date',
        y='Amount',
        color='Category',
        title=f'Scatter Plot for {category}' if category != 'Total' else 'Scatter Plot for All Categories'
    )
    
    fig.update_layout(
        plot_bgcolor='#2e2e36',
        paper_bgcolor='#2e2e36',
        title={
            'text': f'Scatter Plot for {category}' if category != 'Total' else 'Scatter Plot for All Categories',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white'}
        },
        title_font_color='white',
        xaxis=dict(
            title='Date',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title='Amount',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        ),
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    return fig

# Define the app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(src="https://static.vecteezy.com/system/resources/previews/007/984/249/non_2x/stock-market-or-forex-trading-graph-in-graphic-concept-suitable-for-financial-investment-or-economic-trends-business-idea-and-all-art-work-design-abstract-finance-background-illustration-vector.jpg",style={"display": "block", "marginLeft": "auto", "marginRight": "auto", "width": "50%", "height": "auto", "marginTop": "20%"}),
                        html.H2("Personal Expenses Dashboard",style={"marginTop": "40%", "color": "white"},className="text-center"),
                        html.P("Some descriptive text about the dashboard.",style={"marginTop": "20%", "color": "white"},className="text-center"),
                    ],
                    width=3,
                    style={'backgroundColor': '#3b3a42'}
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Tabs(
                                            id="tabs",
                                            value='Groceries',
                                            children=[
                                                dcc.Tab(label='Groceries', value='Groceries', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Shopping', value='Shopping', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Restaurants', value='Restaurants', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Drinks', value='Drinks', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Transport', value='Transport', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Entertainment', value='Entertainment', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Fuel', value='Fuel', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='HealthCare', value='HealthCare', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='SelfCare', value='SelfCare', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                                dcc.Tab(label='Total Spending', value='Total', style={'backgroundColor': '#29292b', 'padding': '10px', 'font-size': '12px'}, selected_style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '10px', 'font-size': '12px'}),
                                            ],
                                            style={'backgroundColor': '#1e1e1e'},
                                        ),
                                        dcc.Graph(
                                            id='pie-chart',
                                            style={'backgroundColor': '#1e1e1e', 'border-bottom': '1px solid #444', 'marginBottom': '10px'}
                                        ),
                                    ],
                                    width=6,
                                    style={'border-right': '1px solid #444'}
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Expense Table",style={"marginBottom": "20px", "color": "white", 'textAlign': 'center', 'marginTop': '20px'}),
                                        dash_table.DataTable(
                                            id='table',
                                            columns=[{"name": i, "id": i} for i in df.columns],
                                            data=df.to_dict('records'),
                                            style_table={'height': '300px', 'overflowY': 'auto', 'width': '100%', 'margin': '0 auto', 'backgroundColor': '#2e2e36'},
                                            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', "textAlign": "center", 'position': 'sticky', 'top': 0, 'zIndex': 1},
                                            style_cell={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white', 'textAlign': 'center'}
                                        ),
                                    ],
                                    width=6
                                ),
                            ],
                            style={'border-bottom': '1px solid #444'}
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id='bar-chart',
                                        style={'backgroundColor': '#1e1e1e', 'border-bottom': '1px solid #444', 'border-right': '1px solid #444', 'marginTop': '10px'}
                                    ),
                                    width=6
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id='scatter-chart',
                                        style={'backgroundColor': '#1e1e1e', 'border-bottom': '1px solid #444', 'border-left': '1px solid #444', 'paddingTop': '10px'}
                                    ),
                                    width=6
                                ),
                            ],
                            style={'border-top': '1px solid #444', 'marginTop': '30px'}
                        ),
                    ],
                    width=9
                ),
            ]
        ),
    ],
    fluid=True
)

# Callback function to update the pie chart, bar chart, and scatter chart based on the selected tab
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('scatter-chart', 'figure')],
    [Input('tabs', 'value')]
)
def update_charts(selected_tab):
    # Generate figures for pie chart, bar chart, and scatter chart based on the selected tab
    pie_fig = create_pie_chart(selected_tab)
    bar_fig = create_bar_chart(selected_tab)
    scatter_fig = create_scatter_plot(selected_tab)
    return pie_fig, bar_fig, scatter_fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
