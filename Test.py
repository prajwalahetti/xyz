import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to classify records
def classify_records(df):
    classified_data = []
    unclassified_records = []
    
    for name, group in df.groupby('Name'):
        group['timestamp'] = pd.to_datetime(group['timestamp'])
        timestamps = group['timestamp'].dt.to_pydatetime()
        
        # Calculate frequency counts
        frequency = { 'daily': 0, 'weekly': 0, 'monthly': 0 }
        
        # Daily classification
        daily_weeks = []
        for week in range(7):  # Check for 7 weeks
            start_date = timestamps.min() + timedelta(weeks=week)
            end_date = start_date + timedelta(days=6)
            week_records = [t for t in timestamps if start_date <= t <= end_date]
            daily_weeks.append(set(t.date() for t in week_records))
        
        daily_count = sum(len(week) >= 5 for week in daily_weeks)
        if daily_count >= 7:
            frequency['daily'] += 1
        
        # Weekly classification
        weekly_weeks = []
        for week in range(9):  # Check for 9 weeks
            start_date = timestamps.min() + timedelta(weeks=week)
            end_date = start_date + timedelta(days=6)
            week_records = [t for t in timestamps if start_date <= t <= end_date]
            weekly_weeks.append(len(week_records) > 0)
        
        if sum(weekly_weeks) >= 9:
            frequency['weekly'] += 1
        
        # Monthly classification
        monthly_counts = {}
        for t in timestamps:
            month_key = t.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        if len(monthly_counts) >= 3:
            frequency['monthly'] += 1
        
        # Determine type and calculate statistics
        record_type = None
        if frequency['daily'] > 0:
            record_type = 'Daily'
            mean_time = group['timestamp'].dt.hour.mean() * 60 + group['timestamp'].dt.minute.mean()
            std_dev_time = group['timestamp'].dt.hour.std() * 60 + group['timestamp'].dt.minute.std()
            classified_data.append([name, frequency['daily'], record_type, mean_time, std_dev_time, list(timestamps)])
        elif frequency['weekly'] > 0:
            record_type = 'Weekly'
            mean_time = group['timestamp'].dt.hour.mean() * 60 + group['timestamp'].dt.minute.mean()
            std_dev_time = group['timestamp'].dt.hour.std() * 60 + group['timestamp'].dt.minute.std()
            classified_data.append([name, frequency['weekly'], record_type, mean_time, std_dev_time, list(timestamps)])
        elif frequency['monthly'] > 0:
            record_type = 'Monthly'
            mean_time = group['timestamp'].dt.hour.mean() * 60 + group['timestamp'].dt.minute.mean()
            std_dev_time = group['timestamp'].dt.hour.std() * 60 + group['timestamp'].dt.minute.std()
            classified_data.append([name, frequency['monthly'], record_type, mean_time, std_dev_time, list(timestamps)])
        else:
            unclassified_records.append([name, list(timestamps)])
            logging.warning(f"Unclassified records for {name}: {list(timestamps)}")

    return classified_data, unclassified_records

def main(input_csv, output_csv):
    try:
        df = pd.read_csv(input_csv, names=['Name', 'timestamp'])
        df.dropna(inplace=True)  # Handle missing values
        classified_data, unclassified_records = classify_records(df)

        # Create DataFrame for classified data
        classified_df = pd.DataFrame(classified_data, columns=['Name', 'Frequency', 'Type', 'Mean Time', 'Standard Deviation', 'Timestamps Considered'])
        unclassified_df = pd.DataFrame(unclassified_records, columns=['Name', 'Timestamps Considered'])

        # Save results to CSV
        classified_df.to_csv(output_csv, index=False)
        unclassified_df.to_csv('unclassified_records.csv', index=False)

        logging.info("Classification completed. Results saved to CSV.")
    
    except Exception as e:
        logging.error(f"Error processing the CSV file: {e}")

if __name__ == "__main__":
    input_csv = 'input.csv'  # Update with your input file
    output_csv = 'classified_records.csv'  # Output file for classified records
    main(input_csv, output_csv)
