# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 10:01:52 2025

@author: SAMC_S25
"""

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html

# Load data from GitHub
def load_data():
    url = "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/filtered_percentile_df.json"
    return pd.read_json(url)

# Create app
app = Dash(__name__)
app.title = "Peer Analysis Dashboard"

# Prepare figure
df = load_data()
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['Portfolio  Date'],
    y=df['Peer_Index_Adjusted_36M'],
    mode='lines',
    name='Peer Index Adjusted 36M'
))

fig.update_layout(
    title="Peer Index Adjusted Performance",
    xaxis_title="Date",
    yaxis_title="Value (%)",
    template="plotly_white"
)

# Layout
app.layout = html.Div([
    html.H1("Peer Analysis Dashboard"),
    dcc.Graph(figure=fig)
])

server = app.server  # Required for Render

if __name__ == "__main__":
    app.run(debug=True)

