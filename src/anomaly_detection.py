import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json


class AnomalyDetector:
    """
    detect significant deviations in mental health search patterns
    
    psychological rationale: anomalies may indicate collective stress responses
    to major societal events, reflecting acute increases in psychological distress
    or help-seeking behavior following trauma exposure or crisis situations.
    """
    def __init__(self):
        self.anomalies = {}
        # major events that may trigger collective psychological responses
        self.major_events = {
            '2020-03-11': 'WHO declares COVID-19 pandemic',
            '2020-03-15': 'US lockdowns begin',
            '2020-11-03': 'US election',
            '2021-01-06': 'US Capitol attack',
            '2022-02-24': 'Ukraine war begins',
            '2023-03-10': 'Silicon Valley Bank collapse',
            '2024-01-01': 'New year mental health awareness'
        }
    
    def zscore_detection(self, series, threshold=2.5):
        """
        detect statistical outliers based on standard deviation
        threshold=2.5 captures observations beyond 98.8th percentile
        """
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        
        anomalies = series[z_scores > threshold]
        return anomalies
    
    def modified_zscore_detection(self, series, threshold=3.5):
        """
        robust anomaly detection using median absolute deviation
        less sensitive to extreme outliers than standard z-score
        """
        median = series.median()
        mad = np.median(np.abs(series - median))
        
        if mad == 0:
            return pd.Series(dtype=float)
        
        modified_z_scores = 0.6745 * (series - median) / mad
        anomalies = series[np.abs(modified_z_scores) > threshold]
        
        return anomalies
    
    def isolation_forest_detection(self, series, contamination=0.05):
        """
        machine learning approach to anomaly detection
        contamination=0.05 assumes 5% of observations are anomalous
        """
        data = series.values.reshape(-1, 1)
        
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        predictions = iso_forest.fit_predict(data)
        anomaly_mask = predictions == -1
        
        anomalies = series[anomaly_mask]
        return anomalies
    
    def rolling_statistics_detection(self, series, window=12, threshold=2.5):
        """detect anomalies using rolling statistics"""
        rolling_mean = series.rolling(window=window, center=True).mean()
        rolling_std = series.rolling(window=window, center=True).std()
        
        z_scores = np.abs((series - rolling_mean) / rolling_std)
        anomalies = series[z_scores > threshold]
        
        return anomalies
    
    def detect_all_methods(self, series, name):
        """run all detection methods"""
        methods = {
            'zscore': self.zscore_detection(series),
            'modified_zscore': self.modified_zscore_detection(series),
            'isolation_forest': self.isolation_forest_detection(series),
            'rolling_stats': self.rolling_statistics_detection(series)
        }
        
        consensus_dates = set()
        for method, anomalies in methods.items():
            consensus_dates.update(anomalies.index)
        
        consensus_count = {}
        for date in consensus_dates:
            count = sum(1 for anomalies in methods.values() if date in anomalies.index)
            consensus_count[date] = count
        
        high_confidence = {date: count for date, count in consensus_count.items() if count >= 3}
        
        self.anomalies[name] = {
            'methods': methods,
            'high_confidence': high_confidence
        }
        
        return self.anomalies[name]
    
    def analyze_covid_impact(self, df, terms):
        """
        quantify pandemic impact on mental health information-seeking
        
        psychological context: establishes pre-pandemic baseline to measure
        the magnitude of psychological distress response to collective trauma.
        increases from baseline reflect both actual distress and reduced stigma
        facilitating help-seeking behavior.
        """
        covid_start = '2020-03-01'
        pre_covid = '2019-01-01'
        
        results = {}
        
        for term in terms:
            if term in df.columns:
                pre = df.loc[pre_covid:covid_start, term].mean()
                during = df.loc[covid_start:, term].mean()
                
                pct_change = ((during - pre) / pre) * 100
                peak = df.loc[covid_start:, term].max()
                peak_date = df.loc[covid_start:, term].idxmax()
                
                results[term] = {
                    'pre_covid_avg': pre,
                    'during_covid_avg': during,
                    'percent_change': pct_change,
                    'peak_value': peak,
                    'peak_date': str(peak_date)
                }
        
        return results
    
    def correlate_with_events(self, anomalies_df, window_days=14):
        """match anomalies with known events"""
        correlations = []
        
        for date_str, event in self.major_events.items():
            event_date = pd.to_datetime(date_str)
            
            window_start = event_date - pd.Timedelta(days=window_days)
            window_end = event_date + pd.Timedelta(days=window_days)
            
            nearby_anomalies = anomalies_df[
                (anomalies_df.index >= window_start) & 
                (anomalies_df.index <= window_end)
            ]
            
            if not nearby_anomalies.empty:
                correlations.append({
                    'event': event,
                    'event_date': date_str,
                    'anomaly_count': len(nearby_anomalies),
                    'terms_affected': nearby_anomalies.columns.tolist()
                })
        
        return correlations
    
    def generate_report(self, df, terms):
        """comprehensive anomaly report"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'terms_analyzed': terms,
            'anomalies_by_term': {},
            'covid_impact': {},
            'event_correlations': []
        }
        
        all_anomalies = []
        
        for term in terms:
            if term in df.columns:
                print(f"analyzing {term}...")
                result = self.detect_all_methods(df[term], term)
                
                report['anomalies_by_term'][term] = {
                    'total_anomalies': len(result['high_confidence']),
                    'dates': [str(d) for d in result['high_confidence'].keys()]
                }
                
                for date in result['high_confidence'].keys():
                    all_anomalies.append({
                        'date': date,
                        'term': term,
                        'value': df.loc[date, term]
                    })
        
        report['covid_impact'] = self.analyze_covid_impact(df, terms)
        
        if all_anomalies:
            anomalies_df = pd.DataFrame(all_anomalies).set_index('date')
            anomalies_df.index = pd.to_datetime(anomalies_df.index)
            
            correlations = self.correlate_with_events(anomalies_df)
            report['event_correlations'] = correlations
        
        return report


def main():
    print("loading data for anomaly detection...")
    df = pd.read_csv('data/processed/clean_trends.csv', index_col=0, parse_dates=True)
    
    detector = AnomalyDetector()
    
    terms = ['depression', 'anxiety', 'therapy', 'burnout']
    
    print("\nrunning anomaly detection...")
    report = detector.generate_report(df, terms)
    
    print("\n" + "="*60)
    print("ANOMALY DETECTION REPORT")
    print("="*60)
    
    print("\nCOVID-19 IMPACT:")
    for term, stats in report['covid_impact'].items():
        print(f"\n{term.upper()}:")
        print(f"  pre-covid average: {stats['pre_covid_avg']:.2f}")
        print(f"  during covid average: {stats['during_covid_avg']:.2f}")
        print(f"  change: {stats['percent_change']:+.1f}%")
        print(f"  peak: {stats['peak_value']:.1f} on {stats['peak_date']}")
    
    print("\n" + "="*60)
    print("EVENT CORRELATIONS:")
    for corr in report['event_correlations']:
        print(f"\n{corr['event']} ({corr['event_date']})")
        print(f"  affected terms: {', '.join(corr['terms_affected'])}")
        print(f"  anomaly count: {corr['anomaly_count']}")
    
    print("\n" + "="*60)
    print("ANOMALIES BY TERM:")
    for term, info in report['anomalies_by_term'].items():
        print(f"\n{term}: {info['total_anomalies']} high-confidence anomalies")
    
    with open('data/processed/anomaly_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\nreport saved to data/processed/anomaly_report.json")


if __name__ == '__main__':
    main()
