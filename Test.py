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

# Function to round timedelta to minutes
def round_to_minutes(timedelta_obj):
    if pd.isna(timedelta_obj):
        return np.nan
    total_minutes = int(round(timedelta_obj.total_seconds() / 60))
    return pd.to_timedelta(total_minutes, unit='m')

# Function to calculate mean and standard deviation for daily records based on hours and minutes only
def calculate_mean_std_daily(time_series):
    logging.info("Calculating mean and standard deviation for daily records.")
    
    # Extract only the time (hours and minutes)
    times_only = time_series.dt.time

    # Convert time to total minutes since midnight
    total_minutes = [(t.hour * 60 + t.minute) for t in times_only]
    
    # Convert to a pandas Series for calculations
    time_diffs = pd.Series(total_minutes).diff().dropna()
    
    if time_diffs.empty:
        logging.warning("No time differences available for daily calculation.")
        return np.nan, np.nan
    
    # Calculate mean and standard deviation
    mean_time = time_diffs.mean()
    std_dev = time_diffs.std()
    
    # Convert mean and std deviation back to timedelta format
    mean_timedelta = pd.to_timedelta(mean_time, unit='m') if pd.notna(mean_time) else np.nan
    std_dev_timedelta = pd.to_timedelta(std_dev, unit='m') if pd.notna(std_dev) else np.nan

    return round_to_minutes(mean_timedelta), round_to_minutes(std_dev_timedelta)

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
    group['day_of_week'] = group['timestamp'].dt.dayofweek  # Monday=0, Sunday=6
    
    # Check daily condition: 5/7 days for 7 consecutive weeks
    daily_weeks = group.groupby('week').filter(lambda x: x['day_of_week'].nunique() >= 5)
    daily_series = daily_weeks.groupby('week').size()
    
    if len(daily_series) >= 7 and (daily_series.index.to_series().diff().fillna(1) == 1).astype(int).sum() >= 7:
        mean_time, std_dev = calculate_mean_std_daily(daily_weeks['timestamp'])
        logging.info(f"Classified as daily with {len(daily_weeks)} records.")
        return 'daily', daily_weeks, len(daily_weeks), mean_time, std_dev, ', '.join(daily_weeks['timestamp'].astype(str))

    # Check weekly condition: At least once per week for 9 consecutive weeks
    weekly_group = group.groupby('week').filter(lambda x: len(x) >= 1)
    weekly_series = weekly_group.groupby('week').size()
    
    if len(weekly_series) >= 9 and (weekly_series.index.to_series().diff().fillna(1) == 1).astype(int).sum() >= 9:
        mean_time, std_dev = calculate_mean_std(weekly_group['timestamp'])
        logging.info(f"Classified as weekly with {len(weekly_group)} records.")
        return 'weekly', weekly_group, len(weekly_group), mean_time, std_dev, ', '.join(weekly_group['timestamp'].astype(str))

    # Check monthly condition: At least once per month for 3 consecutive months
    monthly_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).filter(lambda x: len(x) >= 1)
    monthly_series = monthly_group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).size()
    
    if len(monthly_series) >= 3 and (monthly_series.index.to_series().diff().fillna(1) == 1).astype(int).sum() >= 3:
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
