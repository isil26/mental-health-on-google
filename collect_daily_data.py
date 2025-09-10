#!/usr/bin/env python3
"""
collect daily mental health trends data from 2018 to present
this will take 8-12 minutes due to google trends rate limits
"""

import sys
import os
sys.path.insert(0, 'src')

from data_collection import TrendsCollector
from datetime import datetime
import json
import pandas as pd

def main():
    print("="*70)
    print("MENTAL HEALTH SEARCH TRENDS DATA COLLECTION")
    print("="*70)
    print(f"initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"temporal range: 2018-01-01 to present")
    print(f"expected duration: 8-12 minutes\n")
    print("note: do not interrupt - collection process cannot resume from checkpoint")
    print("="*70)
    
    collector = TrendsCollector()
    
    print("\nCOLLECTING DAILY TIME SERIES DATA")
    print("-"*70)
    print("psychological constructs tracked:")
    print("  mood disorders: depression, anxiety")
    print("  treatment-seeking: therapy, counseling, psychiatrist")
    print("  coping & stress: burnout, stress, panic attack")
    print("  awareness: mental health, antidepressants")
    print("-"*70 + "\n")
    
    try:
        # collect with daily granularity from 2018
        time_series_data = collector.collect_all_terms(
            batch_size=5,
            use_daily=True,
            start_date='2018-01-01'
        )
        
        if time_series_data.empty:
            print("\nCOLLECTION FAILED: no data retrieved")
            print("\npossible causes:")
            print("  1. google trends api rate limiting (most common)")
            print("  2. network connectivity interruption")
            print("  3. api interface changes")
            print("\nrecommended actions:")
            print("  1. wait 15-30 minutes before retry")
            print("  2. verify internet connection stability")
            print("  3. consider vpn if rate limited")
            return 1
        
        # save the data
        print("\n" + "="*70)
        print("PERSISTING DATA TO STORAGE")
        print("="*70)
        
        os.makedirs('data/raw', exist_ok=True)
        time_series_data.to_csv('data/raw/mental_health_trends.csv')
        print(f"saved: data/raw/mental_health_trends.csv")
        
        # calculate pre-covid baseline
        pre_covid = time_series_data[time_series_data.index < '2020-03-01']
        covid_period = time_series_data[
            (time_series_data.index >= '2020-03-01') & 
            (time_series_data.index < '2021-07-01')
        ]
        post_covid = time_series_data[time_series_data.index >= '2021-07-01']
        
        # create metadata
        metadata = {
            'collection_date': datetime.now().isoformat(),
            'terms_collected': list(time_series_data.columns),
            'granularity': 'daily',
            'total_records': len(time_series_data),
            'date_range': {
                'start': str(time_series_data.index[0]),
                'end': str(time_series_data.index[-1]),
                'days': (time_series_data.index[-1] - time_series_data.index[0]).days
            },
            'periods': {
                'pre_covid': {
                    'records': len(pre_covid),
                    'start': str(pre_covid.index[0]) if len(pre_covid) > 0 else None,
                    'end': str(pre_covid.index[-1]) if len(pre_covid) > 0 else None
                },
                'covid': {
                    'records': len(covid_period),
                    'start': str(covid_period.index[0]) if len(covid_period) > 0 else None,
                    'end': str(covid_period.index[-1]) if len(covid_period) > 0 else None
                },
                'post_covid': {
                    'records': len(post_covid),
                    'start': str(post_covid.index[0]) if len(post_covid) > 0 else None,
                    'end': str(post_covid.index[-1]) if len(post_covid) > 0 else None
                }
            }
        }
        
        with open('data/raw/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"saved: data/raw/metadata.json")
        
        # print summary
        print("\n" + "="*70)
        print("DATA COLLECTION COMPLETE")
        print("="*70)
        print(f"total observations: {len(time_series_data):,}")
        print(f"psychological constructs: {len(time_series_data.columns)}")
        print(f"temporal coverage: {time_series_data.index[0].date()} to {time_series_data.index[-1].date()}")
        print(f"observation days: {(time_series_data.index[-1] - time_series_data.index[0]).days:,}")
        print(f"sampling frequency: daily")
        print()
        print("temporal segmentation for baseline analysis:")
        print(f"  pre-pandemic baseline: {len(pre_covid):,} observations")
        print(f"  acute pandemic period: {len(covid_period):,} observations")
        print(f"  post-acute period: {len(post_covid):,} observations")
        print()
        print("next pipeline steps:")
        print("  1. python src/preprocessing.py       # feature engineering")
        print("  2. python src/models.py              # forecasting models")
        print("  3. python src/anomaly_detection.py   # deviation analysis")
        print("  4. streamlit run app.py              # interactive dashboard")
        print("="*70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\ncollection interrupted by user")
        print("note: restart required (api does not support resume from checkpoint)")
        return 1
        
    except Exception as e:
        print(f"\ncollection error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
