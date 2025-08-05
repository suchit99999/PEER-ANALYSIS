# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 10:01:52 2025
@author: SAMC_S25
"""

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table

# ---------------------------
# Load data from GitHub
# ---------------------------
def load_data():
    url = "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/filtered_percentile_df.json"
    return pd.read_json(url)

# Load chart data
filtered_percentile_df = load_data()

# Load table data
merged_weights_comparison = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/merged_weights_comparison.json"
)

# Load sector weight data (replace with your actual source)
sector_weight_df = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/sector_weight_df.json"
)


# ---------------------------
# Create Dash app
# ---------------------------
app = Dash(__name__)
app.title = "Peer Analysis Dashboard"

# ---------------------------
# Build chart
# ---------------------------
timeframe_suffixes = {
    '12M': '12M',
    '36M': '36M',
    '60M': '60M'
}

fig = go.Figure()
for tf_label, suffix in timeframe_suffixes.items():
    visible = tf_label == '36M'  # Show only 36M by default
    fig.add_trace(go.Scatter(
        x=filtered_percentile_df['Portfolio  Date'],
        y=filtered_percentile_df[f'Q1_{suffix}_Adjusted'] * 100,
        name=f'Quartile 1 ({tf_label})',
        line=dict(color='green'),
        visible=visible
    ))
    fig.add_trace(go.Scatter(
        x=filtered_percentile_df['Portfolio  Date'],
        y=filtered_percentile_df[f'Median_{suffix}_Adjusted'] * 100,
        name=f'Median ({tf_label})',
        line=dict(color='orange'),
        visible=visible
    ))
    fig.add_trace(go.Scatter(
        x=filtered_percentile_df['Portfolio  Date'],
        y=filtered_percentile_df[f'Q3_{suffix}_Adjusted'] * 100,
        name=f'Quartile 3 ({tf_label})',
        line=dict(color='blue'),
        visible=visible
    ))
    fig.add_trace(go.Scatter(
        x=filtered_percentile_df['Portfolio  Date'],
        y=filtered_percentile_df[f'Peer_Index_Adjusted_{suffix}'] * 100,
        name=f'Peer Index ({tf_label})',
        line=dict(color='black', dash='dot'),
        visible=visible
    ))

# Dropdown buttons
dropdown_buttons = []
for i, (tf_label, suffix) in enumerate(timeframe_suffixes.items()):
    vis = [False] * len(timeframe_suffixes) * 4
    start = i * 4
    vis[start:start+4] = [True] * 4
    dropdown_buttons.append(dict(
        label=f'{tf_label} View',
        method='update',
        args=[{'visible': vis},
              {'title': f'Rolling {tf_label} Performance (Relative to Median)'}]
    ))

fig.update_layout(
    updatemenus=[dict(
        buttons=dropdown_buttons,
        direction='down',
        showactive=True,
        x=1.15,
        y=1.15
    )],
    title='Rolling 36M Performance (Relative to Median)',
    xaxis_title='Date',
    yaxis_title='Performance Relative to Median (%)',
    template='plotly_white',
    height=600
)

# ---------------------------
# Chart 2: Sector Active Weights (new code you sent)
# ---------------------------
import plotly.graph_objects as go

# Step 1: Sort dates
all_dates = sorted(sector_weight_df['Next_Portfolio_Date'].dropna().unique())

# Step 2: Prepare traces for each date
fig_sector = go.Figure()

for i, date in enumerate(all_dates):
    weights_on_date = (
        sector_weight_df[sector_weight_df['Next_Portfolio_Date'] == date]
        .sort_values('Active_Weight', ascending=False)
    )
    
    bar = go.Bar(
        x=weights_on_date['AMFI_Sector'],
        y=weights_on_date['Active_Weight'],
        marker_color=['#1f77b4' if val >= 0 else '#d62728' for val in weights_on_date['Active_Weight']],
        text=weights_on_date['Active_Weight'].round(2),
        textposition='auto',
        textfont=dict(size=12),
        cliponaxis=False,
        name=f"{pd.to_datetime(date).strftime('%Y-%m-%d')}",
        hovertemplate='<b>%{x}</b><br>Active Weight: %{y:.2f}%<extra></extra>',
        visible=True if i == len(all_dates) - 1 else False
    )
    fig_sector.add_trace(bar)

# Step 3: Dropdown buttons
dropdown_buttons_sector = []
for i, date in enumerate(all_dates):
    visibility = [j == i for j in range(len(all_dates))]
    button = dict(
        label=pd.to_datetime(date).strftime('%Y-%m-%d'),
        method='update',
        args=[{'visible': visibility},
              {'title': f'Active Weights by Sector — {pd.to_datetime(date).strftime("%Y-%m-%d")}'}]
    )
    dropdown_buttons_sector.append(button)

# Step 4: Layout for sector chart
fig_sector.update_layout(
    title=f'Active Weights by Sector — {pd.to_datetime(all_dates[-1]).strftime("%Y-%m-%d")}',
    xaxis_title='Sector',
    yaxis_title='Active Weight (%)',
    template='plotly_white',
    height=550,
    margin=dict(t=80, b=60),
    updatemenus=[dict(
        active=len(all_dates) - 1,
        buttons=dropdown_buttons_sector,
        direction='down',
        x=0.01,
        y=1.15,
        xanchor='left',
        yanchor='top',
        showactive=True
    )]
)



# ---------------------------
# Create scrollable table
# ---------------------------
# Round numeric columns to 2 decimal places
merged_weights_comparison = merged_weights_comparison.round(2)

# Create scrollable table
table_component = dash_table.DataTable(
    data=merged_weights_comparison.to_dict('records'),
    columns=[{"name": i, "id": i} for i in merged_weights_comparison.columns],
    style_table={
        'height': '400px',
        'overflowY': 'auto',
        'overflowX': 'auto',
    },
    style_cell={
        'textAlign': 'center',
        'padding': '8px',
        'minWidth': '120px',
        'whiteSpace': 'normal'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    fixed_rows={'headers': True}
)


# ---------------------------
# Layout (now has two graphs + table)
# ---------------------------
app.layout = html.Div([
    html.H1("Peer Analysis Dashboard"),
    dcc.Graph(figure=fig),  # Existing quartile chart
    html.H2("Active Weights by Sector"),
    dcc.Graph(figure=fig_sector),  # New sector chart
    html.H2("Merged Weights Comparison"),
    table_component
])


# ---------------------------
# Run server
# ---------------------------
server = app.server  # Required for deployment

if __name__ == "__main__":
    app.run(debug=True, port=8051)
