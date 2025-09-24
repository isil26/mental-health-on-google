import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def plot_time_series(df, terms, title="Mental Health Search Trends"):
    """interactive line plot for multiple terms"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    
    for i, term in enumerate(terms):
        if term in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[term],
                mode='lines',
                name=term.title(),
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=f'<b>{term.title()}</b><br>Date: %{{x}}<br>Interest: %{{y}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title="Date",
        yaxis_title="Search Interest (0-100)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_forecast(historical, forecast_df, term, show_intervals=True):
    """plot historical data with forecast"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=historical.index,
        y=historical[term],
        mode='lines',
        name='Historical',
        line=dict(color='#2E86AB', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#A23B72', width=2, dash='dash')
    ))
    
    if show_intervals and 'yhat_lower' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(162, 59, 114, 0.2)',
            fill='tonexty',
            name='Confidence Interval',
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title=f"{term.title()} - Forecast",
        xaxis_title="Date",
        yaxis_title="Search Interest",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_seasonality(df, term):
    """visualize seasonal patterns"""
    df_copy = df.copy()
    df_copy['month'] = df_copy.index.month
    df_copy['year'] = df_copy.index.year
    
    monthly_avg = df_copy.groupby('month')[term].mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=monthly_avg.values,
        marker_color='#F18F01',
        name='Average Interest'
    ))
    
    fig.update_layout(
        title=f"{term.title()} - Seasonal Pattern",
        xaxis_title="Month",
        yaxis_title="Average Search Interest",
        template='plotly_white',
        height=400
    )
    
    return fig


def plot_anomalies(df, term, anomalies, events=None):
    """highlight anomalies on time series"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[term],
        mode='lines',
        name=term.title(),
        line=dict(color='#2E86AB', width=2)
    ))
    
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies.index,
            y=anomalies.values,
            mode='markers',
            name='Anomalies',
            marker=dict(color='#C1292E', size=10, symbol='x'),
            hovertemplate='<b>Anomaly</b><br>Date: %{x}<br>Value: %{y}<extra></extra>'
        ))
    
    if events:
        for date_str, event_name in events.items():
            event_date = pd.to_datetime(date_str)
            if event_date in df.index:
                fig.add_vline(
                    x=event_date,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=event_name,
                    annotation_position="top"
                )
    
    fig.update_layout(
        title=f"{term.title()} - Anomaly Detection",
        xaxis_title="Date",
        yaxis_title="Search Interest",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_correlation_heatmap(df, terms):
    """correlation matrix between terms"""
    corr_matrix = df[terms].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Term Correlation Matrix",
        template='plotly_white',
        height=500,
        width=600
    )
    
    return fig


def plot_geographic_distribution(geo_df, term):
    """choropleth map of search interest"""
    fig = go.Figure(data=go.Choropleth(
        locations=geo_df.index,
        z=geo_df[term],
        locationmode='country names',
        colorscale='Viridis',
        colorbar_title="Interest",
        hovertemplate='<b>%{location}</b><br>Interest: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{term.title()} - Geographic Distribution",
        geo=dict(showframe=False, projection_type='natural earth'),
        height=500
    )
    
    return fig


def plot_model_comparison(metrics_df):
    """compare model performance"""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('MAE', 'RMSE', 'MAPE'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
    )
    
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    models = metrics_df.index
    
    if 'mae' in metrics_df.columns:
        fig.add_trace(go.Bar(
            x=models,
            y=metrics_df['mae'],
            marker_color=colors[0],
            showlegend=False
        ), row=1, col=1)
    
    if 'rmse' in metrics_df.columns:
        fig.add_trace(go.Bar(
            x=models,
            y=metrics_df['rmse'],
            marker_color=colors[1],
            showlegend=False
        ), row=1, col=2)
    
    if 'mape' in metrics_df.columns:
        fig.add_trace(go.Bar(
            x=models,
            y=metrics_df['mape'],
            marker_color=colors[2],
            showlegend=False
        ), row=1, col=3)
    
    fig.update_layout(
        title_text="Model Performance Comparison",
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_decomposition(df, term):
    """seasonal decomposition visualization"""
    from statsmodels.tsa.seasonal import seasonal_decompose
    
    result = seasonal_decompose(df[term].dropna(), model='additive', period=52)
    
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Original', 'Trend', 'Seasonal', 'Residual'),
        vertical_spacing=0.08
    )
    
    fig.add_trace(go.Scatter(x=df.index, y=df[term], mode='lines', name='Original'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=result.trend, mode='lines', name='Trend'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=result.seasonal, mode='lines', name='Seasonal'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=result.resid, mode='lines', name='Residual'), row=4, col=1)
    
    fig.update_layout(
        title_text=f"{term.title()} - Seasonal Decomposition",
        height=800,
        showlegend=False,
        template='plotly_white'
    )
    
    return fig
