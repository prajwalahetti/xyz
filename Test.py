import pandas as pd

# Load the CSV file
df = pd.read_csv('your_file.csv')

# Convert the 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Function to calculate mean and standard deviation of time differences for daily records (based on hours and minutes only)
def calculate_mean_std_daily(time_series):
    # Extract hours and minutes from the timestamps
    times_only = time_series.dt.hour * 60 + time_series.dt.minute  # Convert time to total minutes in a day
    
    # Calculate the time differences
    time_diffs = times_only.diff().dropna()  # Differences in minutes between times
    mean_time = time_diffs.mean()  # Mean of the time differences (in minutes)
    std_dev = time_diffs.std()  # Standard deviation of time differences (in minutes)
    
    # Convert mean and std dev from minutes to a timedelta object for easier interpretation
    mean_timedelta = pd.to_timedelta(mean_time, unit='m') if pd.notna(mean_time) else pd.NaT
    std_dev_timedelta = pd.to_timedelta(std_dev, unit='m') if pd.notna(std_dev) else pd.NaT
    return mean_timedelta, std_dev_timedelta

# Function to find mean and standard deviation of time differences for general series
def calculate_mean_std(time_series):
    time_diffs = time_series.diff().dropna()  # Calculate time differences
    mean_time = time_diffs.mean()  # Mean of the time differences
    std_dev = time_diffs.std()  # Standard deviation of the time differences
    return mean_time, std_dev

# Function to classify records into daily, weekly, or monthly, ensuring exclusivity
def classify_records(group):
    # Extract only the hour and minute for daily consideration
    group['time_only'] = group['timestamp'].dt.time
    
    # Check if the group fits the daily pattern (at least 5 days with the same time)
    daily_group = group.groupby([group['timestamp'].dt.date, 'time_only']).filter(lambda x: len(x) >= 5)
    
    if len(daily_group) > 0:
        # Use daily-specific function for mean and std dev based on hours and minutes
        return 'daily', daily_group, len(daily_group), calculate_mean_std_daily(daily_group['timestamp']), ', '.join(daily_group['timestamp'].astype(str))

    # Check if the group fits the weekly pattern (at least 1 occurrence per week)
    weekly_group = group.groupby(group['timestamp'].dt.isocalendar().week).filter(lambda x: len(x) >= 1)
    
    if len(weekly_group) > 0:
        return 'weekly', weekly_group, len(weekly_group), calculate_mean_std(weekly_group['timestamp']), ', '.join(weekly_group['timestamp'].astype(str))

    # Check if the group fits the monthly pattern (at least 1 occurrence per month)
    monthly_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).filter(lambda x: len(x) >= 1)
    
    if len(monthly_group) > 0:
        return 'monthly', monthly_group, len(monthly_group), calculate_mean_std(monthly_group['timestamp']), ', '.join(monthly_group['timestamp'].astype(str))

    return None, None, 0, (pd.NaT, pd.NaT), ''  # No classification if no group matches

# Initialize lists to collect result data and unclassified records
results = []
unclassified_records = []

# Group data by 'Name' to calculate stats for each person
for name, group in df.groupby('Name'):
    # Sort by timestamp for proper time difference calculations
    group = group.sort_values('timestamp')
    
    # Classify records into daily, weekly, or monthly
    record_type, valid_group, frequency, (mean_time, std_dev), timestamps_considered = classify_records(group)
    
    if record_type:
        # Append classified result for each name
        results.append({
            'Name': name,
            'Frequency': frequency,
            'Type': record_type,
            'Mean Time': mean_time,
            'Standard Deviation': std_dev,
            'Timestamps Considered': timestamps_considered
        })
    else:
        # If no classification, add to unclassified records
        for ts in group['timestamp']:
            unclassified_records.append({
                'Name': name,
                'Timestamp': ts
            })

# Create DataFrames for classified results and unclassified records
results_df = pd.DataFrame(results)
unclassified_df = pd.DataFrame(unclassified_records)

# Export the results to CSV files
results_df.to_csv('classified_output.csv', index=False)
unclassified_df.to_csv('unclassified_output.csv', index=False)

# Print the DataFrames to verify the results
print("Classified Records:")
print(results_df)
print("\nUnclassified Records:")
print(unclassified_df)
