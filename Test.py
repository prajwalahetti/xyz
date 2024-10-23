import pandas as pd
import numpy as np
import logging

# Set up logging configuration
logging.basicConfig(
    filename='classification_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the CSV file
logging.info("Loading CSV file.")
df = pd.read_csv('your_file.csv')

# Convert the 'timestamp' column to datetime format
logging.info("Converting 'timestamp' column to datetime format.")
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')  # Use 'coerce' to handle invalid dates

# Function to calculate mean and standard deviation for daily records based on hours and minutes only
def calculate_mean_std_daily(time_series):
    logging.info("Calculating mean and standard deviation for daily records.")

    # Extract hours and minutes
    total_minutes = time_series.dt.hour * 60 + time_series.dt.minute

    if total_minutes.empty:
        logging.warning("No total minutes available for daily calculation.")
        return np.nan, np.nan

    # Calculate mean and standard deviation
    mean_time = total_minutes.mean()
    std_dev = total_minutes.std()

    # Convert mean and std deviation back to timedelta format
    mean_timedelta = pd.to_timedelta(mean_time, unit='m')
    std_dev_timedelta = pd.to_timedelta(std_dev, unit='m')

    return round_to_minutes(mean_timedelta), round_to_minutes(std_dev_timedelta)

# Function to round timedelta to the nearest minute
def round_to_minutes(timedelta_obj):
    if pd.isna(timedelta_obj):
        return np.nan
    total_minutes = int(round(timedelta_obj.total_seconds() / 60))
    return pd.to_timedelta(total_minutes, unit='m')

# Function to calculate mean and standard deviation for general records
def calculate_mean_std(time_series):
    logging.info("Calculating mean and standard deviation for general records.")
    time_diffs = time_series.diff().dropna()
    if time_diffs.empty:
        logging.warning("No time differences available for general calculation.")
        return np.nan, np.nan
    mean_time = time_diffs.mean()
    std_dev = time_diffs.std()
    mean_timedelta = pd.to_timedelta(mean_time) if pd.notna(mean_time) else np.nan
    std_dev_timedelta = pd.to_timedelta(std_dev) if pd.notna(std_dev) else np.nan
    return round_to_minutes(mean_timedelta), round_to_minutes(std_dev_timedelta)

# Function to classify daily, weekly, or monthly
def classify_records(group):
    logging.info(f"Classifying records for group with {len(group)} entries.")
    group['week'] = group['timestamp'].dt.isocalendar().week
    group['month'] = group['timestamp'].dt.month

    # Check daily condition: 5/7 days for 7 consecutive weeks
    daily_weeks = group.groupby('week').filter(lambda x: x['timestamp'].dt.day.nunique() >= 5)
    if len(daily_weeks['week'].unique()) >= 7:
        mean_time, std_dev = calculate_mean_std_daily(daily_weeks['timestamp'])
        logging.info(f"Classified as daily with {len(daily_weeks)} records.")
        return 'daily', daily_weeks, len(daily_weeks), mean_time, std_dev, ', '.join(daily_weeks['timestamp'].astype(str))

    # Check weekly condition: At least once per week for 9 consecutive weeks
    weekly_group = group.groupby('week').filter(lambda x: len(x) >= 1)
    if len(weekly_group['week'].unique()) >= 9:
        mean_time, std_dev = calculate_mean_std(weekly_group['timestamp'])
        logging.info(f"Classified as weekly with {len(weekly_group)} records.")
        return 'weekly', weekly_group, len(weekly_group), mean_time, std_dev, ', '.join(weekly_group['timestamp'].astype(str))

    # Check monthly condition: At least once per month for 3 consecutive months
    monthly_group = group.groupby(['timestamp'].dt.year, 'month').filter(lambda x: len(x) >= 1)
    if len(monthly_group['month'].unique()) >= 3:
        mean_time, std_dev = calculate_mean_std(monthly_group['timestamp'])
        logging.info(f"Classified as monthly with {len(monthly_group)} records.")
        return 'monthly', monthly_group, len(monthly_group), mean_time, std_dev, ', '.join(monthly_group['timestamp'].astype(str))

    # If no classification, return unclassified
    logging.warning(f"Records for group could not be classified. Group size: {len(group)}.")
    return 'unclassified', group, 0, np.nan, np.nan, ', '.join(group['timestamp'].astype(str))

# Initialize list to collect result data
results = []

# Group data by 'Name' to calculate stats for each person
for name, group in df.groupby('Name'):
    logging.info(f"Processing records for {name}.")
    group = group.sort_values('timestamp')

    # Classify each group
    record_type, valid_group, frequency, mean_time, std_dev, timestamps_considered = classify_records(group)

    # Append the results (classified or unclassified)
    results.append({
        'Name': name,
        'Frequency': frequency if frequency > 0 else '',
        'Type': record_type,
        'Mean Time': mean_time if pd.notna(mean_time) else '',
        'Standard Deviation': std_dev if pd.notna(std_dev) else '',
        'Timestamps Considered': timestamps_considered
    })

# Create DataFrame and export to CSV
logging.info("Writing results to CSV file.")
results_df = pd.DataFrame(results)
results_df.to_csv('output_with_classifications.csv', index=False)

logging.info("Process completed successfully.")

# Print results
print(results_df)
