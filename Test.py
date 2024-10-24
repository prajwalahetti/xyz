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

# Function to calculate mean and standard deviation for days of the week (for weekly)
def calculate_mean_std_weekly(time_series):
    logging.info("Calculating mean and standard deviation for weekly records (day of the week).")
    
    # Extract day of the week (Monday=0, Sunday=6)
    day_of_week = time_series.dt.dayofweek

    if day_of_week.empty:
        logging.warning("No days of the week available for weekly calculation.")
        return np.nan, np.nan

    # Calculate mean and standard deviation based on day of the week
    mean_day = day_of_week.mean()
    std_dev_day = day_of_week.std()

    return round(mean_day, 2), round(std_dev_day, 2)

# Function to calculate mean and standard deviation for weeks of the month (for monthly)
def calculate_mean_std_monthly(time_series):
    logging.info("Calculating mean and standard deviation for monthly records (week of the month).")

    # Extract week of the month (1st, 2nd, etc.)
    week_of_month = (time_series.dt.day - 1) // 7 + 1

    if week_of_month.empty:
        logging.warning("No weeks of the month available for monthly calculation.")
        return np.nan, np.nan

    # Calculate mean and standard deviation based on the week of the month
    mean_week = week_of_month.mean()
    std_dev_week = week_of_month.std()

    return round(mean_week, 2), round(std_dev_week, 2)

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
        mean_day, std_dev_day = calculate_mean_std_weekly(weekly_group['timestamp'])
        logging.info(f"Classified as weekly with {len(weekly_group)} records.")
        return 'weekly', weekly_group, len(weekly_group), mean_day, std_dev_day, ', '.join(weekly_group['timestamp'].astype(str))

    # Check monthly condition: At least once per month for 3 consecutive months
    monthly_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).filter(lambda x: len(x) >= 1)
    if len(monthly_group['month'].unique()) >= 3:
        mean_week, std_dev_week = calculate_mean_std_monthly(monthly_group['timestamp'])
        logging.info(f"Classified as monthly with {len(monthly_group)} records.")
        return 'monthly', monthly_group, len(monthly_group), mean_week, std_dev_week, ', '.join(monthly_group['timestamp'].astype(str))

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
        'Mean Time/Day/Week': mean_time if pd.notna(mean_time) else '',
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
