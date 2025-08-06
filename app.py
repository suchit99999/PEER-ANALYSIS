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
    url = "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/filtered_percentile_df.json"
    return pd.read_json(url)

# Load chart data
filtered_percentile_df = load_data()

# Load table data
merged_weights_comparison = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/merged_weights_comparison.json"
)

# Load JSON
sector_weight_df = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/sector_weight_df.json"
)

# If the JSON stores dates as epoch milliseconds
if pd.api.types.is_numeric_dtype(sector_weight_df['Next_Portfolio_Date']):
    sector_weight_df['Next_Portfolio_Date'] = pd.to_datetime(
        sector_weight_df['Next_Portfolio_Date'], unit='ms', errors='coerce'
    )
else:
    # If stored as string format
    sector_weight_df['Next_Portfolio_Date'] = pd.to_datetime(
        sector_weight_df['Next_Portfolio_Date'], errors='coerce'
    )

# Drop NaT values
sector_weight_df = sector_weight_df.dropna(subset=['Next_Portfolio_Date'])


# Load JSON
plot_data_peer = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/plot_data_peer.json"
)

# If the JSON stores dates as epoch milliseconds
if pd.api.types.is_numeric_dtype(plot_data_peer['Portfolio  Date']):
    plot_data_peer['Portfolio  Date'] = pd.to_datetime(
        plot_data_peer['Portfolio  Date'], unit='ms', errors='coerce'
    )
else:
    # If stored as string format
    plot_data_peer['Portfolio  Date'] = pd.to_datetime(
        plot_data_peer['Portfolio  Date'], errors='coerce'
    )

# Drop NaT values
plot_data_peer = plot_data_peer.dropna(subset=['Portfolio  Date'])

# Load JSON
plot_data = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/plot_data.json"
)

# If the JSON stores dates as epoch milliseconds
if pd.api.types.is_numeric_dtype(plot_data['Portfolio  Date']):
    plot_data['Portfolio  Date'] = pd.to_datetime(
        plot_data['Portfolio  Date'], unit='ms', errors='coerce'
    )
else:
    # If stored as string format
    plot_data['Portfolio  Date'] = pd.to_datetime(
        plot_data['Portfolio  Date'], errors='coerce'
    )

# Drop NaT values
plot_data = plot_data.dropna(subset=['Portfolio  Date'])

# Load JSON
pivot_avg = pd.read_json(
    "https://raw.githubusercontent.com/suchit99999/PEER-ANALYSIS/main/MULTI%20ASSET/pivot_avg.json"
)

# If the JSON stores dates as epoch milliseconds
if pd.api.types.is_numeric_dtype(pivot_avg['Portfolio  Date']):
    pivot_avg['Portfolio  Date'] = pd.to_datetime(
        pivot_avg['Portfolio  Date'], unit='ms', errors='coerce'
    )
else:
    # If stored as string format
    pivot_avg['Portfolio  Date'] = pd.to_datetime(
        pivot_avg['Portfolio  Date'], errors='coerce'
    )

# Drop NaT values
pivot_avg = pivot_avg.dropna(subset=['Portfolio  Date'])


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
# import plotly.graph_objects as go

# # Step 1: Sort dates (Fix: ensure proper datetime format)
# sector_weight_df['Next_Portfolio_Date'] = pd.to_datetime(
#     sector_weight_df['Next_Portfolio_Date'], errors='coerce'
# )

# # Drop NaT values
# sector_weight_df = sector_weight_df.dropna(subset=['Next_Portfolio_Date'])


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

# =============================
# Chart 3: Top Active Weight Changes
# =============================

# Ensure date column is datetime
sector_weight_df['Next_Portfolio_Date'] = pd.to_datetime(sector_weight_df['Next_Portfolio_Date'], errors='coerce')

# Step 2: Get sorted unique dates (excluding the first one)
all_dates_changes = sorted(sector_weight_df['Next_Portfolio_Date'].dropna().unique())[1:]

# Step 3: Prepare Plotly figure with dropdown traces
fig_changes = go.Figure()

for i, date in enumerate(all_dates_changes):
    weights_on_date = (
        sector_weight_df[sector_weight_df['Next_Portfolio_Date'] == date]
        .dropna(subset=['Active_Weight_Change'])
        .sort_values('Active_Weight_Change', ascending=False)
        .head(10)
    )
    
    bar = go.Bar(
        x=weights_on_date['AMFI_Sector'],
        y=weights_on_date['Active_Weight_Change'],
        marker_color=['#1f77b4' if val >= 0 else '#d62728' for val in weights_on_date['Active_Weight_Change']],
        text=weights_on_date['Active_Weight_Change'].round(2),
        textposition='auto',
        name=date.strftime('%Y-%m-%d'),
        visible=True if i == len(all_dates_changes) - 1 else False,
        hovertemplate='<b>%{x}</b><br>Change in Active Weight: %{y:.2f}%<extra></extra>'
    )
    
    fig_changes.add_trace(bar)

# Step 4: Create dropdown
dropdown_buttons_changes = []
for i, date in enumerate(all_dates_changes):
    visibility = [j == i for j in range(len(all_dates_changes))]
    dropdown_buttons_changes.append(dict(
        label=date.strftime('%Y-%m-%d'),
        method='update',
        args=[{'visible': visibility},
              {'title': f'Top Active Weight Changes — {date.strftime("%Y-%m-%d")}'}]
    ))

# Step 5: Layout
fig_changes.update_layout(
    title=f'Top Active Weight Changes — {all_dates_changes[-1].strftime("%Y-%m-%d")}',
    xaxis_title='Sector',
    yaxis_title='Change in Active Weight (%)',
    template='plotly_white',
    height=600,
    margin=dict(t=80, b=60),
    updatemenus=[dict(
        active=len(all_dates_changes) - 1,
        buttons=dropdown_buttons_changes,
        direction='down',
        x=0.01,
        y=1.15,
        xanchor='left',
        yanchor='top',
        showactive=True
    )]
)

import plotly.express as px

# =============================
# Chart 4: Tracking Error vs Peer Benchmark
# =============================

highlight_scheme = 'Shriram Flexi Cap Fund (G)'

# Ensure dates are parsed
plot_data_peer['Portfolio  Date'] = pd.to_datetime(plot_data_peer['Portfolio  Date'], errors='coerce')

unique_schemes = sorted(plot_data_peer['Scheme Name'].unique())

# Step 2: Color map
color_palette = px.colors.qualitative.Dark24 + px.colors.qualitative.Set3 + px.colors.qualitative.Set2
color_map = {scheme: color_palette[i % len(color_palette)] for i, scheme in enumerate(unique_schemes)}
color_map[highlight_scheme] = 'red'  # Shriram stays red

# Step 3: Build Plotly figure
fig_tracking_error = go.Figure()

for scheme in unique_schemes:
    df_scheme = plot_data_peer[plot_data_peer['Scheme Name'] == scheme]

    fig_tracking_error.add_trace(go.Scatter(
        x=df_scheme['Portfolio  Date'],
        y=df_scheme['Tracking_Error_%'],
        mode='lines',
        name=scheme,
        line=dict(
            color=color_map[scheme],
            width=2 if scheme == highlight_scheme else 1.5,
            dash='solid'
        ),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>%{text}<br>TE (Peer): %{y:.2f}%',
        text=[scheme] * len(df_scheme),
        visible=True if scheme == highlight_scheme else 'legendonly'
    ))

# Step 4: Layout
fig_tracking_error.update_layout(
    title='Tracking Error With Peer Benchmark Over Time',
    xaxis_title='Date',
    yaxis_title='Tracking Error vs Peer Benchmark (%)',
    template='plotly_white',
    hovermode='x unified',
    height=650,
    legend_title='Click schemes to toggle'
)

import plotly.express as px

# =============================
# Chart 5: Tracking Error Over Time (All Schemes)
# =============================

highlight_scheme = 'Shriram Flexi Cap Fund (G)'

# Ensure date column is datetime
plot_data['Portfolio  Date'] = pd.to_datetime(plot_data['Portfolio  Date'], errors='coerce')

unique_schemes = sorted(plot_data['Scheme Name'].unique())

# Step 2: Define color palette
color_palette = px.colors.qualitative.Dark24 + px.colors.qualitative.Set3 + px.colors.qualitative.Set2
color_map = {scheme: color_palette[i % len(color_palette)] for i, scheme in enumerate(unique_schemes)}

# Override highlight scheme to red
color_map[highlight_scheme] = 'red'

# Step 3: Build figure
fig_tracking_error_all = go.Figure()

for scheme in unique_schemes:
    df_scheme = plot_data[plot_data['Scheme Name'] == scheme]
    
    fig_tracking_error_all.add_trace(go.Scatter(
        x=df_scheme['Portfolio  Date'],
        y=df_scheme['Tracking_Error_%'],
        mode='lines',
        name=scheme,
        line=dict(
            color=color_map[scheme],
            width=2 if scheme == highlight_scheme else 1.5,
            dash='solid'
        ),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>%{text}<br>TE: %{y:.2f}%',
        text=[scheme] * len(df_scheme),
        visible=True if scheme == highlight_scheme else 'legendonly'
    ))

# Step 4: Layout
fig_tracking_error_all.update_layout(
    title='Tracking Error With Nifty 500',
    xaxis_title='Date',
    yaxis_title='Tracking Error (%)',
    template='plotly_white',
    hovermode='x unified',
    height=650,
    legend_title='Click schemes to toggle'
)

import plotly.io as pio

# =============================
# Chart 6: Average Investment Category Allocation
# =============================

# Ensure Portfolio Date is datetime
pivot_avg["Portfolio  Date"] = pd.to_datetime(pivot_avg["Portfolio  Date"], errors="coerce")

# Create figure
fig_avg_allocation = go.Figure()

# Loop over only the category columns (exclude the date column)
for category in pivot_avg.columns.drop("Portfolio  Date"):
    fig_avg_allocation.add_trace(
        go.Scatter(
            x=pivot_avg["Portfolio  Date"],  # use actual dates
            y=pivot_avg[category],
            mode="lines",
            name=category,
            fill="tozeroy"
        )
    )

fig_avg_allocation.update_layout(
    title="Average Investment Category Allocation Across All Schemes",
    xaxis_title="Date",
    yaxis_title="Average Weight (%)",
    legend_title="Investment Category",
    height=600,
    template="plotly_white"
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

    # Chart 6 becomes first chart
    html.H2("Average Investment Category Allocation Across All Schemes"),
    dcc.Graph(figure=fig_avg_allocation),


    html.H2("Active Weights by Sector"),
    dcc.Graph(figure=fig_sector),  # Chart 2

    html.H2("Top Active Weight Changes"),
    dcc.Graph(figure=fig_changes),  # Chart 3
    
    html.H2("Merged Weights Comparison"),
    table_component,

    html.H2("Tracking Error With Peer Benchmark Over Time"),
    dcc.Graph(figure=fig_tracking_error),  # Chart 4

    html.H2("Tracking Error Over Time (All Schemes)"),
    dcc.Graph(figure=fig_tracking_error_all),  # Chart 5

    
    html.H2("Rolling Quartile Performance"),
    dcc.Graph(figure=fig),  # Chart 1 (now second)
])


# ---------------------------
# Run server
# ---------------------------
server = app.server  # Required for deployment

import webbrowser

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8051")  # Opens browser automatically
    app.run(debug=True, port=8051)

