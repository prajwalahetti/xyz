import pandas as pd

# Load the CSV file
df = pd.read_csv('your_file.csv')

# Convert the 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Function to round timedelta to minutes
def round_to_minutes(timedelta_obj):
    if pd.isna(timedelta_obj):
        return pd.NaT
    total_minutes = int(round(timedelta_obj.total_seconds() / 60))
    return pd.to_timedelta(total_minutes, unit='m')

# Function to calculate mean and standard deviation for daily records based on hours and minutes only
def calculate_mean_std_daily(time_series):
    times_only = time_series.dt.hour * 60 + time_series.dt.minute
    time_diffs = times_only.diff().dropna()
    mean_time = time_diffs.mean()
    std_dev = time_diffs.std()
    if pd.notna(mean_time):
        mean_timedelta = pd.to_timedelta(mean_time, unit='m')
    else:
        mean_timedelta = pd.NaT
    if pd.notna(std_dev):
        std_dev_timedelta = pd.to_timedelta(std_dev, unit='m')
    else:
        std_dev_timedelta = pd.NaT
    return round_to_minutes(mean_timedelta), round_to_minutes(std_dev_timedelta)

# Function to calculate mean and standard deviation for general records
def calculate_mean_std(time_series):
    time_diffs = time_series.diff().dropna()
    mean_time = time_diffs.mean()
    std_dev = time_diffs.std()
    if pd.notna(mean_time):
        mean_timedelta = pd.to_timedelta(mean_time)
    else:
        mean_timedelta = pd.NaT
    if pd.notna(std_dev):
        std_dev_timedelta = pd.to_timedelta(std_dev)
    else:
        std_dev_timedelta = pd.NaT
    return round_to_minutes(mean_timedelta), round_to_minutes(std_dev_timedelta)

# Function to classify daily, weekly, or monthly
def classify_records(group):
    group['week'] = group['timestamp'].dt.isocalendar().week
    group['day_of_week'] = group['timestamp'].dt.dayofweek  # Monday=0, Sunday=6
    
    # Check daily condition: 5/7 days for 7 consecutive weeks
    daily_weeks = group.groupby('week').filter(lambda x: x['day_of_week'].nunique() >= 5)
    weekly_series = daily_weeks.groupby('week').size()
    
    # Check if we have 7 consecutive weeks with daily records
    consecutive_weeks = (weekly_series.index.to_series().diff().fillna(1) == 1).astype(int)
    consecutive_streak = (consecutive_weeks.groupby((consecutive_weeks != 1).cumsum()).cumsum() == 7).any()

    if consecutive_streak:
        mean_time, std_dev = calculate_mean_std_daily(daily_weeks['timestamp'])
        return 'daily', daily_weeks, len(daily_weeks), mean_time, std_dev, ', '.join(daily_weeks['timestamp'].astype(str))

    # Check weekly condition: At least once per week for 9 consecutive weeks
    weekly_group = group.groupby('week').filter(lambda x: len(x) >= 1)
    weekly_series = weekly_group.groupby('week').size()
    
    consecutive_weeks = (weekly_series.index.to_series().diff().fillna(1) == 1).astype(int)
    consecutive_streak = (consecutive_weeks.groupby((consecutive_weeks != 1).cumsum()).cumsum() == 9).any()

    if consecutive_streak:
        mean_time, std_dev = calculate_mean_std(weekly_group['timestamp'])
        return 'weekly', weekly_group, len(weekly_group), mean_time, std_dev, ', '.join(weekly_group['timestamp'].astype(str))

    # Check monthly condition: At least once per month for 3 consecutive months
    monthly_group = group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).filter(lambda x: len(x) >= 1)
    monthly_series = monthly_group.groupby([group['timestamp'].dt.year, group['timestamp'].dt.month]).size()
    
    consecutive_months = (monthly_series.index.to_series().diff().fillna(1) == 1).astype(int)
    consecutive_streak = (consecutive_months.groupby((consecutive_months != 1).cumsum()).cumsum() == 3).any()

    if consecutive_streak:
        mean_time, std_dev = calculate_mean_std(monthly_group['timestamp'])
        return 'monthly', monthly_group, len(monthly_group), mean_time, std_dev, ', '.join(monthly_group['timestamp'].astype(str))

    return None, None, 0, pd.NaT, pd.NaT, ''  # Default return for unclassified records

# Initialize list to collect result data
results = []

# Group data by 'Name' to calculate stats for each person
for name, group in df.groupby('Name'):
    group = group.sort_values('timestamp')
    
    # Ensure classify_records returns proper values, even if no classification occurs
    record_type, valid_group, frequency, mean_time, std_dev, timestamps_considered = classify_records(group)
    
    # Append classified data
    if record_type:
        results.append({
            'Name': name,
            'Frequency': frequency,
            'Type': record_type,
            'Mean Time': mean_time if pd.notna(mean_time) else '',
            'Standard Deviation': std_dev if pd.notna(std_dev) else '',
            'Timestamps Considered': timestamps_considered
        })
    # Append unclassified data
    else:
        for ts in group['timestamp']:
            results.append({
                'Name': name,
                'Frequency': None,
                'Type': None,
                'Mean Time': None,
                'Standard Deviation': None,
                'Timestamps Considered': ts
            })

# Create DataFrame and export to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('output_with_classifications.csv', index=False)

# Print results
print(results_df)
