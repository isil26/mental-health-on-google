import pandas as pd
import numpy as np
from pytrends.request import TrendReq
import time
from datetime import datetime, timedelta
import json
import os


class TrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
        self.mental_health_terms = [
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
    
    def collect_historical_data(self, keywords, timeframe='today 5-y', geo='', retries=3):
        """fetch search trends for given keywords"""
        for attempt in range(retries):
            try:
                self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
                data = self.pytrends.interest_over_time()
                
                if not data.empty:
                    data = data.drop('isPartial', axis=1, errors='ignore')
                    print(f"  ✓ collected {len(data)} records for {keywords}")
                    time.sleep(3)
                    return data
                else:
                    print(f"  ⚠ no data returned for {keywords}, attempt {attempt+1}/{retries}")
                    time.sleep(5)
            
            except Exception as e:
                print(f"  ✗ error fetching {keywords}: {e}")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"  waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"  failed after {retries} attempts")
        
        return pd.DataFrame()
    
    def collect_daily_data_chunked(self, keywords, start_date='2018-01-01', retries=3):
        """
        collect daily data by splitting into 6-month chunks
        google trends limits daily data to ~9 months per request
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime('today')
        all_chunks = []
        
        # create 6-month chunks
        current = start
        while current < end:
            chunk_end = min(current + timedelta(days=180), end)
            timeframe = f"{current.strftime('%Y-%m-%d')} {chunk_end.strftime('%Y-%m-%d')}"
            
            print(f"  fetching {current.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")
            
            for attempt in range(retries):
                try:
                    self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='')
                    chunk_data = self.pytrends.interest_over_time()
                    
                    if not chunk_data.empty:
                        chunk_data = chunk_data.drop('isPartial', axis=1, errors='ignore')
                        all_chunks.append(chunk_data)
                        print(f"    ✓ got {len(chunk_data)} daily records")
                        time.sleep(5)  # be nice to google
                        break
                    else:
                        print(f"    ⚠ no data, attempt {attempt+1}/{retries}")
                        time.sleep(10)
                
                except Exception as e:
                    print(f"    ✗ error: {e}")
                    if attempt < retries - 1:
                        time.sleep(15)
            
            current = chunk_end + timedelta(days=1)
        
        if not all_chunks:
            return pd.DataFrame()
        
        # combine all chunks
        combined = pd.concat(all_chunks)
        combined = combined[~combined.index.duplicated(keep='first')]
        combined = combined.sort_index()
        
        return combined
    
    def collect_by_region(self, keywords, timeframe='today 5-y'):
        """get geographic distribution"""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe)
            regional = self.pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True)
            time.sleep(2)
            return regional
        
        except Exception as e:
            print(f"error fetching regional data: {e}")
            return pd.DataFrame()
    
    def collect_all_terms(self, batch_size=5, use_daily=True, start_date='2018-01-01'):
        """
        collect data for all mental health terms
        use_daily=True: ~2500+ daily samples from 2018-2025 (recommended!)
        use_daily=False: ~260 weekly samples from last 5 years
        """
        all_data = {}
        
        if use_daily:
            expected_days = (pd.to_datetime('today') - pd.to_datetime(start_date)).days
            print(f"\ncollecting DAILY observations from {start_date} to present")
            print(f"   expected observations: ~{expected_days}")
            print(f"   estimated duration: 5-10 minutes (api rate limits)\n")
        
        for i in range(0, len(self.mental_health_terms), batch_size):
            batch = self.mental_health_terms[i:i+batch_size]
            print(f"\nprocessing batch {i//batch_size + 1}: {', '.join(batch)}")
            
            if use_daily:
                data = self.collect_daily_data_chunked(batch, start_date=start_date)
            else:
                data = self.collect_historical_data(batch)
            
            if not data.empty:
                for term in batch:
                    if term in data.columns:
                        all_data[term] = data[term]
                        print(f"  collected {term}: {len(data)} records")
            else:
                # fallback to individual terms
                print(f"  batch collection failed, attempting individual retrieval...")
                for term in batch:
                    if use_daily:
                        single_data = self.collect_daily_data_chunked([term], start_date=start_date)
                    else:
                        single_data = self.collect_historical_data([term])
                    
                    if not single_data.empty and term in single_data.columns:
                        all_data[term] = single_data[term]
                        print(f"  collected {term}: {len(single_data)} records")
                    time.sleep(5)
            
            print(f"  rate limit delay before next batch...")
            time.sleep(10)
        
        if not all_data:
            raise ValueError("failed to collect any data. check internet connection or try again later.")
        
        df = pd.DataFrame(all_data)
        print(f"\nTOTAL COLLECTED: {len(df)} records across {len(df.columns)} constructs")
        print(f"temporal range: {df.index.min()} to {df.index.max()}")
        
        return df
    
    def collect_geographic_data(self):
        """collect regional breakdown for key terms"""
        key_terms = ['depression', 'anxiety', 'therapy', 'burnout']
        regional_data = {}
        
        for term in key_terms:
            print(f"collecting regional data for: {term}")
            data = self.collect_by_region([term])
            if not data.empty:
                regional_data[term] = data[term]
            time.sleep(3)
        
        return pd.DataFrame(regional_data)
    
    def save_data(self, data, filename):
        """save collected data"""
        os.makedirs('data/raw', exist_ok=True)
        filepath = f'data/raw/{filename}'
        data.to_csv(filepath)
        print(f"saved to {filepath}")


def main():
    print("="*60)
    print("GOOGLE TRENDS DATA COLLECTION")
    print("="*60)
    print(f"timestamp: {datetime.now()}")
    print("\nnote: this takes 10-15 minutes due to rate limits")
    print("google trends limits requests to prevent abuse")
    print("please be patient...\n")
    
    collector = TrendsCollector()
    
    print("="*60)
    print("1. COLLECTING TIME SERIES DATA")
    print("="*60)
    try:
        time_series_data = collector.collect_all_terms()
        
        if len(time_series_data) == 0:
            print("\nno data collected. this usually means:")
            print("  - google trends is rate limiting you")
            print("  - internet connection issue")
            print("  - pytrends api issue")
            print("\nsolutions:")
            print("  - wait 10-15 minutes and try again")
            print("  - check your internet connection")
            print("  - try a vpn if blocked")
            return
        
        collector.save_data(time_series_data, 'mental_health_trends.csv')
        print(f"\ntime series data collected: {len(time_series_data)} records")
    
    except Exception as e:
        print(f"\ntime series collection failed: {e}")
        return
    
    print("\n" + "="*60)
    print("2. COLLECTING GEOGRAPHIC DATA")
    print("="*60)
    try:
        geographic_data = collector.collect_geographic_data()
        collector.save_data(geographic_data, 'geographic_trends.csv')
        print(f"\ngeographic data collected for {len(geographic_data)} countries")
    except Exception as e:
        print(f"\ngeographic collection failed: {e}")
        print("continuing with time series data only...")
    
    # calculate pre-covid baseline
    pre_covid = time_series_data[time_series_data.index < '2020-03-01']
    covid_period = time_series_data[
        (time_series_data.index >= '2020-03-01') & 
        (time_series_data.index < '2021-07-01')
    ]
    post_covid = time_series_data[time_series_data.index >= '2021-07-01']
    
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
    
    print("\n" + "="*60)
    print("COLLECTION COMPLETE!")
    print("="*60)
    print(f"✓ total records: {len(time_series_data)}")
    print(f"✓ terms collected: {len(time_series_data.columns)}")
    print(f"✓ date range: {time_series_data.index[0]} to {time_series_data.index[-1]}")
    print(f"✓ data saved to: data/raw/")
    print("="*60)


if __name__ == '__main__':
    main()
