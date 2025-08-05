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
# Create scrollable table
# ---------------------------
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
# Layout
# ---------------------------
app.layout = html.Div([
    html.H1("Peer Analysis Dashboard"),
    dcc.Graph(figure=fig),
    html.H2("Merged Weights Comparison"),
    table_component
])

# ---------------------------
# Run server
# ---------------------------
server = app.server  # Required for deployment

if __name__ == "__main__":
    app.run(debug=True, port=8051)
