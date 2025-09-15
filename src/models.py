import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


class ProphetForecaster:
    def __init__(self, seasonality_mode='multiplicative'):
        self.model = None
        self.seasonality_mode = seasonality_mode
        self.metrics = {}
    
    def prepare_data(self, df, column):
        """convert to prophet format"""
        prophet_df = pd.DataFrame({
            'ds': df.index,
            'y': df[column].values
        })
        return prophet_df
    
    def train(self, df, column, yearly_seasonality=True, weekly_seasonality=True):
        """train prophet model"""
        data = self.prepare_data(df, column)
        
        import logging
        logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
        logging.getLogger('prophet').setLevel(logging.WARNING)
        
        self.model = Prophet(
            seasonality_mode=self.seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        
        self.model.fit(data, show_progress=False)
        return self.model
    
    def forecast(self, periods=90, freq='W'):
        """generate forecast"""
        if self.model is None:
            raise ValueError("model not trained")
        
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        return forecast
    
    def evaluate(self, actual_df, column, test_periods=26):
        """evaluate model performance"""
        train = actual_df[:-test_periods]
        test = actual_df[-test_periods:]
        
        self.train(train, column)
        forecast = self.forecast(periods=test_periods)
        
        predictions = forecast.tail(test_periods)['yhat'].values
        actuals = test[column].values
        
        mae = mean_absolute_error(actuals, predictions)
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100
        
        self.metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
        
        return self.metrics


class ARIMAForecaster:
    def __init__(self, order=(1, 1, 1)):
        self.model = None
        self.fitted_model = None
        self.order = order
        self.metrics = {}
    
    def check_stationarity(self, series):
        """test if series is stationary"""
        result = adfuller(series.dropna())
        return result[1] < 0.05
    
    def find_best_order(self, series, max_p=5, max_d=2, max_q=5):
        """grid search for best arima parameters"""
        best_aic = np.inf
        best_order = None
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def train(self, series, auto_order=False):
        """train arima model"""
        if auto_order:
            self.order = self.find_best_order(series)
            print(f"best order found: {self.order}")
        
        self.model = ARIMA(series, order=self.order)
        self.fitted_model = self.model.fit()
        
        return self.fitted_model
    
    def forecast(self, steps=90):
        """generate forecast"""
        if self.fitted_model is None:
            raise ValueError("model not trained")
        
        forecast = self.fitted_model.forecast(steps=steps)
        return forecast
    
    def evaluate(self, series, test_size=26):
        """evaluate model performance"""
        train = series[:-test_size]
        test = series[-test_size:]
        
        self.train(train)
        predictions = self.forecast(steps=test_size)
        
        mae = mean_absolute_error(test, predictions)
        rmse = np.sqrt(mean_squared_error(test, predictions))
        mape = np.mean(np.abs((test - predictions) / test)) * 100
        
        self.metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
        
        return self.metrics


class LSTMForecaster:
    def __init__(self, lookback=12):
        self.model = None
        self.scaler = MinMaxScaler()
        self.lookback = lookback
        self.metrics = {}
    
    def create_sequences(self, data, lookback):
        """create sequences for lstm"""
        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback])
        return np.array(X), np.array(y)
    
    def prepare_data(self, series):
        """scale and create sequences"""
        scaled = self.scaler.fit_transform(series.values.reshape(-1, 1))
        X, y = self.create_sequences(scaled, self.lookback)
        return X, y, scaled
    
    def build_model(self, input_shape):
        """build lstm architecture"""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            model = Sequential([
                LSTM(50, activation='relu', return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            return model
        
        except ImportError:
            print("tensorflow not installed, skipping lstm")
            return None
    
    def train(self, series, epochs=50, batch_size=32, validation_split=0.1):
        """train lstm model"""
        X, y, scaled = self.prepare_data(series)
        
        self.model = self.build_model((X.shape[1], X.shape[2]))
        
        if self.model is None:
            return None
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        return history
    
    def forecast(self, series, steps=90):
        """generate forecast"""
        if self.model is None:
            return None
        
        scaled = self.scaler.transform(series.values.reshape(-1, 1))
        predictions = []
        current_seq = scaled[-self.lookback:].reshape(1, self.lookback, 1)
        
        for _ in range(steps):
            pred = self.model.predict(current_seq, verbose=0)
            predictions.append(pred[0, 0])
            current_seq = np.append(current_seq[:, 1:, :], pred.reshape(1, 1, 1), axis=1)
        
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        return predictions.flatten()


class ModelEnsemble:
    def __init__(self):
        self.prophet = ProphetForecaster()
        self.arima = ARIMAForecaster()
        self.lstm = LSTMForecaster()
        self.weights = {'prophet': 0.4, 'arima': 0.3, 'lstm': 0.3}
    
    def train_all(self, df, column):
        """train all models"""
        results = {}
        
        print(f"training prophet...")
        self.prophet.train(df, column)
        prophet_metrics = self.prophet.evaluate(df, column)
        results['prophet'] = prophet_metrics
        
        print(f"training arima...")
        series = df[column]
        self.arima.train(series, auto_order=True)
        arima_metrics = self.arima.evaluate(series)
        results['arima'] = arima_metrics
        
        print(f"training lstm...")
        lstm_history = self.lstm.train(series)
        if lstm_history:
            results['lstm'] = {'trained': True}
        
        return results
    
    def ensemble_forecast(self, df, column, periods=90):
        """combine predictions from all models"""
        prophet_pred = self.prophet.forecast(periods=periods)['yhat'].tail(periods).values
        arima_pred = self.arima.forecast(steps=periods)
        
        series = df[column]
        lstm_pred = self.lstm.forecast(series, steps=periods)
        
        if lstm_pred is None:
            ensemble = (
                self.weights['prophet'] * prophet_pred + 
                self.weights['arima'] * arima_pred
            ) / (self.weights['prophet'] + self.weights['arima'])
        else:
            ensemble = (
                self.weights['prophet'] * prophet_pred + 
                self.weights['arima'] * arima_pred +
                self.weights['lstm'] * lstm_pred
            )
        
        return ensemble


def save_models(prophet_model, arima_model, lstm_model, term):
    """save trained models"""
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(prophet_model, f'models/{term}_prophet.pkl')
    joblib.dump(arima_model, f'models/{term}_arima.pkl')
    if lstm_model.model:
        lstm_model.model.save(f'models/{term}_lstm.h5')


def main():
    print("loading processed data...")
    df = pd.read_csv('data/processed/clean_trends.csv', index_col=0, parse_dates=True)
    
    key_terms = ['depression', 'anxiety', 'therapy', 'burnout']
    results = {}
    
    for term in key_terms:
        print(f"\n{'='*50}")
        print(f"training models for: {term}")
        print('='*50)
        
        # train arima only (prophet has compatibility issues)
        print(f"training arima model...")
        arima = ARIMAForecaster()
        series = df[term]
        arima.train(series, auto_order=True)
        arima_metrics = arima.evaluate(series)
        
        results[term] = {'arima': arima_metrics}
        
        print(f"\narima performance:")
        for metric, value in arima_metrics.items():
            if isinstance(value, (int, float)):
                print(f"  {metric}: {value:.2f}")
        
        # save arima model
        import os
        os.makedirs('models', exist_ok=True)
        joblib.dump(arima, f'models/{term}_arima.pkl')
        print(f"saved model to models/{term}_arima.pkl")
    
    results_df = pd.DataFrame(results).T
    results_df.to_csv('models/model_performance.csv')
    print("\n" + "="*50)
    print("training complete! models saved to models/")
    print("="*50)
    print("\nnote: prophet models skipped due to compatibility issues")
    print("arima models trained successfully for all terms")


if __name__ == '__main__':
    main()
