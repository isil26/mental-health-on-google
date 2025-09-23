"""
unit tests for mental health trends project
run with: pytest test_project.py
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append('src')


class TestPreprocessing:
    def test_handle_missing_values(self):
        from preprocessing import TimeSeriesPreprocessor
        
        dates = pd.date_range('2020-01-01', periods=100, freq='W')
        data = pd.DataFrame({
            'depression': np.random.randint(50, 100, 100),
            'anxiety': np.random.randint(50, 100, 100)
        }, index=dates)
        
        data.iloc[10:15, 0] = np.nan
        
        preprocessor = TimeSeriesPreprocessor.__new__(TimeSeriesPreprocessor)
        preprocessor.data = data
        
        result = preprocessor.handle_missing_values()
        
        assert result['depression'].isna().sum() == 0
    
    def test_add_time_features(self):
        from preprocessing import TimeSeriesPreprocessor
        
        dates = pd.date_range('2020-01-01', periods=100, freq='W')
        data = pd.DataFrame({
            'depression': np.random.randint(50, 100, 100)
        }, index=dates)
        
        preprocessor = TimeSeriesPreprocessor.__new__(TimeSeriesPreprocessor)
        result = preprocessor.add_time_features(data)
        
        assert 'year' in result.columns
        assert 'month' in result.columns
        assert 'week' in result.columns


class TestAnomalyDetection:
    def test_zscore_detection(self):
        from anomaly_detection import AnomalyDetector
        
        normal_data = np.random.normal(50, 10, 100)
        normal_data[50] = 150
        
        series = pd.Series(normal_data)
        detector = AnomalyDetector()
        
        anomalies = detector.zscore_detection(series)
        
        assert len(anomalies) > 0
        assert 50 in anomalies.index
    
    def test_isolation_forest(self):
        from anomaly_detection import AnomalyDetector
        
        normal_data = np.random.normal(50, 10, 100)
        series = pd.Series(normal_data)
        
        detector = AnomalyDetector()
        anomalies = detector.isolation_forest_detection(series)
        
        assert isinstance(anomalies, pd.Series)


class TestModels:
    def test_prophet_forecaster(self):
        from models import ProphetForecaster
        
        dates = pd.date_range('2020-01-01', periods=200, freq='W')
        trend = np.linspace(50, 70, 200)
        noise = np.random.normal(0, 5, 200)
        data = pd.DataFrame({
            'value': trend + noise
        }, index=dates)
        
        forecaster = ProphetForecaster()
        model = forecaster.train(data, 'value')
        
        assert forecaster.model is not None
        
        forecast = forecaster.forecast(periods=10)
        assert len(forecast) > 0
        assert 'yhat' in forecast.columns
    
    def test_arima_forecaster(self):
        from models import ARIMAForecaster
        
        series = pd.Series(np.random.randn(100).cumsum() + 50)
        
        forecaster = ARIMAForecaster()
        forecaster.train(series)
        
        assert forecaster.fitted_model is not None
        
        predictions = forecaster.forecast(steps=10)
        assert len(predictions) == 10


class TestDataCollection:
    def test_trends_collector_init(self):
        from data_collection import TrendsCollector
        
        collector = TrendsCollector()
        
        assert collector.pytrends is not None
        assert len(collector.mental_health_terms) > 0
        assert 'depression' in collector.mental_health_terms


class TestVisualizations:
    def test_plot_time_series(self):
        from visualizations import plot_time_series
        
        dates = pd.date_range('2020-01-01', periods=100, freq='W')
        data = pd.DataFrame({
            'depression': np.random.randint(50, 100, 100),
            'anxiety': np.random.randint(50, 100, 100)
        }, index=dates)
        
        fig = plot_time_series(data, ['depression', 'anxiety'])
        
        assert fig is not None
        assert len(fig.data) == 2


def test_config_exists():
    """ensure config file is properly set up"""
    import config
    
    assert hasattr(config, 'MENTAL_HEALTH_TERMS')
    assert hasattr(config, 'PROPHET_PARAMS')
    assert len(config.MENTAL_HEALTH_TERMS) > 0


def test_directory_structure():
    """verify project directories exist"""
    required_dirs = ['data', 'data/raw', 'data/processed', 'models', 'notebooks', 'src']
    
    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"directory {dir_path} missing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
