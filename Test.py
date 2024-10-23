import pandas as pd
import numpy as np
import logging
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(input_csv):
    """Load CSV data into a DataFrame."""
    try:
        df = pd.read_csv(input_csv, names=['Name', 'timestamp'])
        df.dropna(inplace=True)  # Handle missing values
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

def classify_records(df):
    """Classify records into daily, weekly, and monthly categories."""
    classified_data = []
    unclassified_records = []
    
    for name, group in df.groupby('Name'):
        timestamps = group['timestamp']

        frequency = {'daily': 0, 'weekly': 0, 'monthly': 0}
        
        # Daily classification
        if classify_daily(timestamps):
            frequency['daily'] += 1
        
        # Weekly classification
        if classify_weekly(timestamps):
            frequency['weekly'] += 1
        
        # Monthly classification
        if classify_monthly(timestamps):
            frequency['monthly'] += 1
        
        # Determine type and calculate statistics
        record_type, mean_time, std_dev_time = get_statistics(group, frequency)

        if record_type:
            classified_data.append([name, frequency[record_type.lower()], record_type, mean_time, std_dev_time, list(timestamps)])
        else:
            unclassified_records.append([name, list(timestamps)])
            logging.warning(f"Unclassified records for {name}: {list(timestamps)}")

    return classified_data, unclassified_records

def classify_daily(timestamps):
    """Check if records qualify as daily."""
    daily_weeks = []
    for week in range(7):  # Check for 7 weeks
        start_date = timestamps.min() + timedelta(weeks=week)
        end_date = start_date + timedelta(days=6)
        week_records = timestamps[(timestamps >= start_date) & (timestamps <= end_date)]
        daily_weeks.append(set(week_records.dt.date))
    
    daily_count = sum(len(week) >= 5 for week in daily_weeks)
    return daily_count >= 7

def classify_weekly(timestamps):
    """Check if records qualify as weekly."""
    weekly_weeks = []
    for week in range(9):  # Check for 9 weeks
        start_date = timestamps.min() + timedelta(weeks=week)
        end_date = start_date + timedelta(days=6)
        week_records = timestamps[(timestamps >= start_date) & (timestamps <= end_date)]
        weekly_weeks.append(len(week_records) > 0)
    
    return sum(weekly_weeks) >= 9

def classify_monthly(timestamps):
    """Check if records qualify as monthly."""
    monthly_counts = {}
    for t in timestamps:
        month_key = t.strftime('%Y-%m')
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
    
    return len(monthly_counts) >= 3

def get_statistics(group, frequency):
    """Calculate mean time and standard deviation for the classified records."""
    record_type = None
    mean_time = std_dev_time = None

    if frequency['daily'] > 0:
        record_type = 'Daily'
    elif frequency['weekly'] > 0:
        record_type = 'Weekly'
    elif frequency['monthly'] > 0:
        record_type = 'Monthly'

    if record_type:
        mean_time = group['timestamp'].dt.hour.mean() * 60 + group['timestamp'].dt.minute.mean()
        std_dev_time = np.sqrt(group['timestamp'].dt.hour.var()) * 60 + np.sqrt(group['timestamp'].dt.minute.var())
    
    return record_type, mean_time, std_dev_time

def save_results(classified_data, unclassified_records, output_csv):
    """Save classified and unclassified records to CSV."""
    classified_df = pd.DataFrame(classified_data, columns=['Name', 'Frequency', 'Type', 'Mean Time', 'Standard Deviation', 'Timestamps Considered'])
    unclassified_df = pd.DataFrame(unclassified_records, columns=['Name', 'Timestamps Considered'])

    classified_df.to_csv(output_csv, index=False)
    unclassified_df.to_csv('unclassified_records.csv', index=False)

def main(input_csv, output_csv):
    df = load_data(input_csv)
    classified_data, unclassified_records = classify_records(df)
    save_results(classified_data, unclassified_records, output_csv)
    logging.info("Classification completed. Results saved to CSV.")

if __name__ == "__main__":
    input_csv = 'input.csv'  # Update with your input file
    output_csv = 'classified_records.csv'  # Output file for classified records
    main(input_csv, output_csv)
