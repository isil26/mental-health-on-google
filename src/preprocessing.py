import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import os


class TimeSeriesPreprocessor:
    def __init__(self, data_path='data/raw/mental_health_trends.csv'):
        self.data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        self.processed_data = {}
    
    def handle_missing_values(self, method='interpolate'):
        """fill missing values"""
        df = self.data.copy()
        
        if method == 'interpolate':
            df = df.interpolate(method='time', limit_direction='both')
        elif method == 'forward':
            df = df.fillna(method='ffill')
        
        return df
    
    def remove_outliers(self, df, threshold=3.5):
        """remove extreme outliers using modified z-score"""
        df_clean = df.copy()
        
        for col in df.columns:
            median = df[col].median()
            mad = np.median(np.abs(df[col] - median))
            
            if mad != 0:
                modified_z_scores = 0.6745 * (df[col] - median) / mad
                outlier_mask = np.abs(modified_z_scores) > threshold
                df_clean.loc[outlier_mask, col] = np.nan
        
        df_clean = df_clean.interpolate(method='time')
        return df_clean
    
    def add_time_features(self, df):
        """extract temporal features"""
        df = df.copy()
        df['year'] = df.index.year
        df['month'] = df.index.month
        df['week'] = df.index.isocalendar().week
        df['quarter'] = df.index.quarter
        df['day_of_year'] = df.index.dayofyear
        
        return df
    
    def calculate_rolling_stats(self, df, windows=[4, 12, 26]):
        """compute rolling statistics for trend analysis"""
        df_stats = df.copy()
        
        for col in df.columns:
            if col not in ['year', 'month', 'week', 'quarter', 'day_of_year']:
                for window in windows:
                    df_stats[f'{col}_ma{window}'] = df[col].rolling(window=window).mean()
                    df_stats[f'{col}_std{window}'] = df[col].rolling(window=window).std()
        
        return df_stats
    
    def normalize_data(self, df, method='minmax'):
        """normalize time series"""
        df_norm = df.copy()
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if method == 'minmax':
            for col in numeric_cols:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df_norm[col] = (df[col] - min_val) / (max_val - min_val)
        
        elif method == 'zscore':
            for col in numeric_cols:
                df_norm[col] = (df[col] - df[col].mean()) / df[col].std()
        
        return df_norm
    
    def create_lag_features(self, df, lags=[1, 2, 4, 8]):
        """create lagged features for ml models"""
        df_lag = df.copy()
        
        for col in df.columns:
            if col not in ['year', 'month', 'week', 'quarter', 'day_of_year']:
                for lag in lags:
                    df_lag[f'{col}_lag{lag}'] = df[col].shift(lag)
        
        return df_lag.dropna()
    
    def prepare_for_prophet(self, df, column):
        """format data for prophet model"""
        prophet_df = pd.DataFrame({
            'ds': df.index,
            'y': df[column].values
        })
        return prophet_df.reset_index(drop=True)
    
    def process_all(self, save=True):
        """run full preprocessing pipeline"""
        print("preprocessing time series data...")
        
        df = self.handle_missing_values()
        print(f"handled missing values: {df.shape}")
        
        df_clean = self.remove_outliers(df)
        print(f"removed outliers: {df_clean.shape}")
        
        df_features = self.add_time_features(df_clean)
        print(f"added time features: {df_features.shape}")
        
        self.processed_data['clean'] = df_clean
        self.processed_data['with_features'] = df_features
        
        df_stats = self.calculate_rolling_stats(df_clean)
        self.processed_data['with_stats'] = df_stats
        
        if save:
            os.makedirs('data/processed', exist_ok=True)
            
            df_clean.to_csv('data/processed/clean_trends.csv')
            df_features.to_csv('data/processed/trends_with_features.csv')
            df_stats.to_csv('data/processed/trends_with_stats.csv')
            
            print("saved processed data to data/processed/")
        
        return self.processed_data


def main():
    print(f"starting preprocessing: {datetime.now()}")
    
    preprocessor = TimeSeriesPreprocessor()
    processed = preprocessor.process_all(save=True)
    
    print("\npreprocessing complete!")
    print(f"datasets created: {list(processed.keys())}")
    
    clean_df = processed['clean']
    print(f"\ndate range: {clean_df.index[0]} to {clean_df.index[-1]}")
    print(f"terms: {list(clean_df.columns)}")
    print(f"\ndescriptive stats:")
    print(clean_df.describe())


if __name__ == '__main__':
    main()
