import re
import pandas as pd
import logging
from datetime import timedelta

# Set up logging
logging.basicConfig(
    filename='classification_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load main dataset
logging.info("Loading main data CSV file.")
df = pd.read_csv('data.csv')  # Main file in format 'name, feed, timestamp'

# Load name-to-feed mapping file with comma-separated regex patterns
logging.info("Loading name-to-feed mapping file with comma-separated regex patterns.")
name_feed_mapping = pd.read_csv('name_feed_mapping.csv', delimiter=';')  # Format: 'name; feed'

# Initialize lists to store matched and unmatched rows
matched_rows = []
unmatched_rows = []

# Iterate through each row in the main dataset
for idx, row in df.iterrows():
    name = row['name']
    feed = row['feed']
    
    # Filter rows based on the name and corresponding feed regex patterns
    match_found = False
    if name in name_feed_mapping['name'].values:
        # Get the regex patterns for this name, split by commas
        patterns = name_feed_mapping[name_feed_mapping['name'] == name]['feed'].values[0].split(',')
        
        # Check if feed matches any pattern
        for pattern in patterns:
            try:
                if re.match(pattern.strip(), feed):  # Ensure whitespace is trimmed
                    matched_row = row.copy()  # Copy row data
                    matched_row['feed'] = pattern.strip()  # Replace feed with matched regex pattern
                    matched_rows.append(matched_row)
                    match_found = True
                    break
            except re.error as e:
                logging.error(f"Regex error for pattern '{pattern}': {e}")  # Log regex error
                
    # If no match is found for the current row, add it to unmatched_rows
    if not match_found:
        unmatched_rows.append(row)

# Create DataFrames for matched and unmatched entries
df_filtered = pd.DataFrame(matched_rows)
df_unmatched = pd.DataFrame(unmatched_rows)

# Convert timestamp to datetime for matched entries
df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'], errors='coerce')

# Frequency Analysis Functions

def analyze_daily(df):
    daily_df = df.groupby(df['timestamp'].dt.date).size().reset_index(name='count')
    if len(daily_df) >= 7:
        for i in range(len(daily_df) - 49 + 1):  # Slide through 7-week windows
            window = daily_df.iloc[i:i + 49]  # 7 weeks = 49 days
            if (window.groupby(window['timestamp'].dt.isocalendar().week).size() >= 5).all():
                # Convert timestamp to minutes for mean and std deviation calculations
                df['time_in_minutes'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
                mean_minutes = df['time_in_minutes'].mean()
                std_minutes = df['time_in_minutes'].std()
                
                # Convert back to hours and minutes
                mean_hours, mean_minutes = divmod(mean_minutes, 60)
                return "daily", f"{int(mean_hours)}:{int(mean_minutes):02d}", std_minutes
    return None

def analyze_weekly(df):
    weekly_df = df.groupby(df['timestamp'].dt.isocalendar().week).size().reset_index(name='count')
    if len(weekly_df) >= 7:
        for i in range(len(weekly_df) - 7 + 1):  # Slide through all 7-week windows
            window = weekly_df.iloc[i:i + 7]  # 7-week window
            if (window['count'] >= 1).all():  # Check if each week has at least one entry
                mean_day = df['timestamp'].dt.day_name().mode()[0]  # Most common day of the week
                std_dev_day = df['timestamp'].dt.day_name().value_counts().std()
                return "weekly", mean_day, std_dev_day
    return None

def analyze_monthly(df):
    monthly_df = df.groupby([df['timestamp'].dt.year, df['timestamp'].dt.month]).size().reset_index(name='count')
    if len(monthly_df) >= 3:
        for i in range(len(monthly_df) - 3 + 1):  # Slide through all 3-month windows
            window = monthly_df.iloc[i:i + 3]  # 3-month window
            if (window['count'] >= 1).all():  # Check if each month has at least one entry
                mean_week = df['timestamp'].dt.isocalendar().week.mean()
                std_dev_week = df['timestamp'].dt.isocalendar().week.std()
                return "monthly", mean_week, std_dev_week
    return None

# Apply Analysis Functions to Each Group
results = []
for (name, feed), group in df_filtered.groupby(['name', 'feed']):
    daily_result = analyze_daily(group)
    if daily_result:
        results.append((name, *daily_result))
        continue
    
    weekly_result = analyze_weekly(group)
    if weekly_result:
        results.append((name, *weekly_result))
        continue
    
    monthly_result = analyze_monthly(group)
    if monthly_result:
        results.append((name, *monthly_result))
    else:
        results.append((name, "unclassified", None, None))

# Convert results to DataFrame
results_df = pd.DataFrame(results, columns=['name', 'frequency', 'mean', 'std_dev'])

# Save results to CSV
logging.info("Saving analysis results to CSV.")
results_df.to_csv('classified_entries_analysis.csv', index=False)
df_unmatched.to_csv('unmatched_entries.csv', index=False)
