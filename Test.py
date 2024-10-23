import pandas as pd

# Load the CSV file
df = pd.read_csv('your_file.csv')

# Convert the 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Function to find mean and standard deviation of time differences for a given series
def calculate_mean_std(time_series):
    time_diffs = time_series.diff().dropna()  # Calculate time differences
    mean_time = time_diffs.mean()  # Mean of the time differences
    std_dev = time_diffs.std()  # Standard deviation of the time differences
    return mean_time, std_dev

# Function to classify records into daily, weekly, or monthly, ensuring exclusivity
def classify_records(group):
    # Check if the group fits the daily pattern (at least 5 days in a week)
    daily_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.isocalendar().week]).filter(lambda x: len(x) >= 5)
    
    if len(daily_group) > 0:
        return 'daily', daily_group, len(daily_group), calculate_mean_std(daily_group['timestamp']), ', '.join(daily_group['timestamp'].astype(str))

    # Check if the group fits the weekly pattern (at least 1 occurrence per week)
    weekly_group = group.groupby(group['timestamp'].dt.isocalendar().week).filter(lambda x: len(x) >= 1)
    
    if len(weekly_group) > 0:
        return 'weekly', weekly_group, len(weekly_group), calculate_mean_std(weekly_group['timestamp']), ', '.join(weekly_group['timestamp'].astype(str))

    # Check if the group fits the monthly pattern (at least 1 occurrence per month)
    monthly_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).filter(lambda x: len(x) >= 1)
    
    if len(monthly_group) > 0:
        return 'monthly', monthly_group, len(monthly_group), calculate_mean_std(monthly_group['timestamp']), ', '.join(monthly_group['timestamp'].astype(str))

    return None, None, 0, (pd.NaT, pd.NaT), ''  # No classification if no group matches

# Initialize list to collect result data
results = []

# Group data by 'Name' to calculate stats for each person
for name, group in df.groupby('Name'):
    # Sort by timestamp for proper time difference calculations
    group = group.sort_values('timestamp')
    
    # Classify records into daily, weekly, or monthly
    record_type, valid_group, frequency, (mean_time, std_dev), timestamps_considered = classify_records(group)
    
    # Append result for each name with its classification
    results.append({
        'Name': name,
        'Frequency': frequency,
        'Type': record_type,
        'Mean Time': mean_time,
        'Standard Deviation': std_dev,
        'Timestamps Considered': timestamps_considered
    })

# Create a new DataFrame for the results
results_df = pd.DataFrame(results)

# Export the results to a CSV file
results_df.to_csv('output_file.csv', index=False)

# Print the DataFrame to verify the results
print(results_df)
