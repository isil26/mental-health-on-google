# configuration file for mental health trends project

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODELS_DIR = BASE_DIR / 'models'
NOTEBOOKS_DIR = BASE_DIR / 'notebooks'

MENTAL_HEALTH_TERMS = [
    'depression',
    'anxiety',
    'therapy',
    'burnout',
    'mental health',
    'panic attack',
    'stress',
    'counseling',
    'psychiatrist',
    'antidepressants'
]

KEY_TERMS = ['depression', 'anxiety', 'therapy', 'burnout']

TIMEFRAME = 'today 5-y'

GEO_LOCATION = ''

MAJOR_EVENTS = {
    '2020-03-11': 'WHO declares COVID-19 pandemic',
    '2020-03-15': 'US lockdowns begin',
    '2020-11-03': 'US election',
    '2021-01-06': 'US Capitol attack',
    '2022-02-24': 'Ukraine war begins',
    '2023-03-10': 'Silicon Valley Bank collapse',
    '2024-01-01': 'New year mental health awareness'
}

PROPHET_PARAMS = {
    'seasonality_mode': 'multiplicative',
    'yearly_seasonality': True,
    'weekly_seasonality': True,
    'daily_seasonality': False,
    'changepoint_prior_scale': 0.05
}

ARIMA_DEFAULT_ORDER = (1, 1, 1)

LSTM_PARAMS = {
    'lookback': 12,
    'epochs': 50,
    'batch_size': 32,
    'validation_split': 0.1
}

ANOMALY_THRESHOLD = 2.5
ANOMALY_CONTAMINATION = 0.05

FORECAST_HORIZON_WEEKS = 26

TEST_SIZE_WEEKS = 26

RANDOM_SEED = 42
