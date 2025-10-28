import argparse
from datetime import datetime
import sys
import os


def collect_data(args):
    """run data collection"""
    from src.data_collection import main
    print("starting data collection...")
    main()


def preprocess_data(args):
    """run preprocessing"""
    from src.preprocessing import main
    print("starting preprocessing...")
    main()


def train_models(args):
    """train forecasting models"""
    from src.models import main
    print("starting model training...")
    main()


def detect_anomalies(args):
    """run anomaly detection"""
    from src.anomaly_detection import main
    print("starting anomaly detection...")
    main()


def run_full_pipeline(args):
    """run complete pipeline"""
    print("="*60)
    print("RUNNING FULL PIPELINE")
    print("="*60)
    
    steps = [
        ("1. data collection", collect_data),
        ("2. preprocessing", preprocess_data),
        ("3. model training", train_models),
        ("4. anomaly detection", detect_anomalies)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}")
        print("-"*60)
        try:
            step_func(args)
            print(f"✓ {step_name} complete")
        except Exception as e:
            print(f"✗ {step_name} failed: {e}")
            if not args.continue_on_error:
                sys.exit(1)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print("\nrun the dashboard with: streamlit run app.py")


def main():
    parser = argparse.ArgumentParser(
        description="mental health trends - pipeline runner"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='command to run')
    
    collect_parser = subparsers.add_parser('collect', help='collect data from google trends')
    
    preprocess_parser = subparsers.add_parser('preprocess', help='preprocess collected data')
    
    train_parser = subparsers.add_parser('train', help='train forecasting models')
    
    anomaly_parser = subparsers.add_parser('anomalies', help='detect anomalies')
    
    pipeline_parser = subparsers.add_parser('pipeline', help='run full pipeline')
    pipeline_parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='continue pipeline even if a step fails'
    )
    
    args = parser.parse_args()
    
    commands = {
        'collect': collect_data,
        'preprocess': preprocess_data,
        'train': train_models,
        'anomalies': detect_anomalies,
        'pipeline': run_full_pipeline
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
