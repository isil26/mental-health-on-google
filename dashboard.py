"""
production-grade analytics dashboard for mental health search trends
simplified version for reliable deployment
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import json
from scipy import stats

# initialize dash application
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Mental Health Trends Analytics"
)
server = app.server

# load data
print("Loading data...")
try:
    df = pd.read_csv('data/processed/clean_trends.csv', index_col=0, parse_dates=True)
    geo_df = pd.read_csv('data/raw/geographic_trends.csv', index_col=0)
    with open('data/processed/anomaly_report.json', 'r') as f:
        anomaly_report = json.load(f)
    print(f"SUCCESS: Loaded {df.shape[0]} observations, {df.shape[1]} constructs")
    DATA_LOADED = True
except Exception as e:
    print(f"ERROR loading data: {e}")
    DATA_LOADED = False
    df = pd.DataFrame()
    geo_df = pd.DataFrame()
    anomaly_report = {}

# define layout
if DATA_LOADED:
    # get available constructs
    constructs = [col for col in df.columns if col not in ['year', 'month', 'week', 'quarter', 'day_of_year']]
    
    app.layout = dbc.Container([
        # header
        dbc.Row([
            dbc.Col([
                html.H1("Mental Health Search Trends Analytics", className="text-center my-4"),
                html.P(
                    "Time series analysis of mental health information-seeking behavior using Google Trends data (2018-2025). "
                    "Search patterns serve as proxy indicators for population-level psychological distress.",
                    className="text-center text-muted mb-4"
                )
            ])
        ]),
        
        # metrics cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Temporal Coverage", className="text-muted"),
                        html.H4(f"{(df.index[-1] - df.index[0]).days // 365} years")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Daily Observations", className="text-muted"),
                        html.H4(f"{len(df):,}")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Constructs Tracked", className="text-muted"),
                        html.H4(f"{len(constructs)}")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Geographic Regions", className="text-muted"),
                        html.H4(f"{len(geo_df)}")
                    ])
                ])
            ], width=3)
        ], className="mb-4"),
        
        # controls
        dbc.Row([
            dbc.Col([
                html.Label("Select Psychological Construct:", className="fw-bold"),
                dcc.Dropdown(
                    id='construct-dropdown',
                    options=[{'label': c.replace('_', ' ').title(), 'value': c} for c in constructs],
                    value='depression',
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Comparison Terms:", className="fw-bold"),
                dcc.Dropdown(
                    id='comparison-dropdown',
                    options=[{'label': c.replace('_', ' ').title(), 'value': c} for c in constructs],
                    value=['anxiety', 'therapy'],
                    multi=True
                )
            ], width=4),
            dbc.Col([
                html.Label("Moving Average (days):", className="fw-bold"),
                dcc.Slider(
                    id='ma-slider',
                    min=7,
                    max=90,
                    step=7,
                    value=30,
                    marks={7: '7', 30: '30', 60: '60', 90: '90'}
                )
            ], width=4)
        ], className="mb-4"),
        
        # main visualization
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Temporal Trends Analysis")),
                    dbc.CardBody([
                        html.P(
                            "Search volume trends reveal population-level changes in mental health awareness, "
                            "help-seeking intentions, and collective psychological distress. Notable spikes often "
                            "correlate with major societal events (e.g., COVID-19 pandemic onset in March 2020).",
                            className="text-muted small"
                        ),
                        dcc.Graph(id='main-trend-plot', style={'height': '500px'})
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # correlation heatmap
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Correlation Matrix")),
                    dbc.CardBody([
                        html.P(
                            "Correlation patterns reveal relationships between different mental health constructs. "
                            "High correlation between symptom terms (depression, anxiety) and treatment terms (therapy, counseling) "
                            "suggests coordinated help-seeking behavior following distress recognition.",
                            className="text-muted small"
                        ),
                        dcc.Graph(id='correlation-heatmap', style={'height': '500px'})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Geographic Distribution")),
                    dbc.CardBody([
                        html.P(
                            "Geographic variation reflects cultural differences in mental health literacy, stigma, "
                            "and healthcare access. Higher search volumes indicate awareness and help-seeking propensity.",
                            className="text-muted small"
                        ),
                        dcc.Graph(id='geo-plot', style={'height': '500px'})
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        # anomaly detection
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Anomaly Detection - Crisis Events")),
                    dbc.CardBody([
                        html.P(
                            "Statistical anomalies (>2.5σ from mean) represent potential collective stress responses. "
                            "The March 2020 spike across multiple terms reflects acute psychological impact of COVID-19 pandemic onset.",
                            className="text-muted small"
                        ),
                        dcc.Graph(id='anomaly-plot', style={'height': '400px'})
                    ])
                ])
            ])
        ]),
        
        html.Footer([
            html.Hr(className="mt-5"),
            html.P(
                "Data: Google Trends API (2018-2025) | Methodology: ARIMA, Facebook Prophet, LSTM | "
                "Psychology: Health Action Process Model, Trauma Psychology Framework",
                className="text-center text-muted small"
            )
        ])
        
    ], fluid=True)
    
else:
    # error layout
    app.layout = dbc.Container([
        dbc.Alert([
            html.H4("Data Loading Error", className="alert-heading"),
            html.P("Required data files could not be loaded."),
            html.Hr(),
            html.P("Run: ./upgrade_data.sh or python collect_daily_data.py", className="mb-0")
        ], color="danger", className="mt-5")
    ])

# callbacks
if DATA_LOADED:
    @app.callback(
        Output('main-trend-plot', 'figure'),
        [Input('construct-dropdown', 'value'),
         Input('comparison-dropdown', 'value'),
         Input('ma-slider', 'value')]
    )
    def update_main_plot(construct, comparisons, ma_window):
        """render main temporal trends plot"""
        fig = go.Figure()
        
        # main construct
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[construct],
            name=construct.replace('_', ' ').title(),
            mode='lines',
            line=dict(width=2)
        ))
        
        # moving average
        ma = df[construct].rolling(window=ma_window).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=ma,
            name=f'{ma_window}-day MA',
            mode='lines',
            line=dict(width=3, dash='dash')
        ))
        
        # comparison terms
        if comparisons:
            for comp in comparisons:
                if comp in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[comp],
                        name=comp.replace('_', ' ').title(),
                        mode='lines',
                        opacity=0.6
                    ))
        
        # mark COVID-19 onset
        fig.add_vline(
            x="2020-03-11",
            line_dash="dash",
            line_color="red",
            annotation_text="COVID-19 Pandemic",
            annotation_position="top"
        )
        
        fig.update_layout(
            title=f"Search Trends: {construct.replace('_', ' ').title()}",
            xaxis_title="Date",
            yaxis_title="Relative Search Interest (0-100)",
            hovermode='x unified',
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    @app.callback(
        Output('correlation-heatmap', 'figure'),
        Input('construct-dropdown', 'value')
    )
    def update_correlation(construct):
        """render correlation heatmap"""
        constructs = [col for col in df.columns if col not in ['year', 'month', 'week', 'quarter', 'day_of_year']]
        corr_matrix = df[constructs].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
            y=[c.replace('_', ' ').title() for c in corr_matrix.index],
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Correlation Between Mental Health Constructs",
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @app.callback(
        Output('geo-plot', 'figure'),
        Input('construct-dropdown', 'value')
    )
    def update_geo(construct):
        """render geographic choropleth"""
        if construct not in geo_df.columns:
            return go.Figure()
        
        fig = go.Figure(data=go.Choropleth(
            locations=geo_df.index,
            z=geo_df[construct],
            locationmode='country names',
            colorscale='Viridis',
            colorbar_title="Search<br>Interest",
            hovertemplate='<b>%{location}</b><br>Interest: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"Global Distribution: {construct.replace('_', ' ').title()}",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            ),
            height=500
        )
        
        return fig
    
    @app.callback(
        Output('anomaly-plot', 'figure'),
        Input('construct-dropdown', 'value')
    )
    def update_anomaly(construct):
        """render anomaly detection plot with z-scores"""
        # calculate z-scores
        mean = df[construct].mean()
        std = df[construct].std()
        z_scores = (df[construct] - mean) / std
        
        fig = go.Figure()
        
        # main line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=z_scores,
            name='Z-Score',
            mode='lines',
            line=dict(color='blue', width=1)
        ))
        
        # anomaly threshold lines
        fig.add_hline(y=2.5, line_dash="dash", line_color="red", annotation_text="Anomaly Threshold (+2.5σ)")
        fig.add_hline(y=-2.5, line_dash="dash", line_color="red", annotation_text="Anomaly Threshold (-2.5σ)")
        
        # highlight anomalies
        anomalies = z_scores[abs(z_scores) > 2.5]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies.index,
                y=anomalies.values,
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        # COVID marker
        fig.add_vline(
            x="2020-03-11",
            line_dash="dash",
            line_color="orange",
            annotation_text="COVID-19"
        )
        
        fig.update_layout(
            title=f"Anomaly Detection: {construct.replace('_', ' ').title()}",
            xaxis_title="Date",
            yaxis_title="Standard Deviations from Mean",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig

# run server
if __name__ == '__main__':
    print(f"\n{'='*60}")
    print("MENTAL HEALTH TRENDS ANALYTICS DASHBOARD")
    print(f"{'='*60}")
    if DATA_LOADED:
        print(f"✓ Data loaded: {len(df)} observations")
        print(f"✓ Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"✓ Constructs: {len([c for c in df.columns if c not in ['year', 'month', 'week', 'quarter', 'day_of_year']])}")
    print(f"\nDashboard running at: http://localhost:8050")
    print(f"{'='*60}\n")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
