import re
import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename='classification_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load main dataset
logging.info("Loading main data CSV file.")
df = pd.read_csv('data.csv')  # Main file format: 'name, feed, timestamp'

# Load name-to-feed mapping file with semicolon-separated regex patterns
logging.info("Loading name-to-feed mapping file.")
name_feed_mapping = pd.read_csv('name_feed_mapping.csv', delimiter=';')  # Format: 'name;feed'

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
                    # If there's a match, store the row with the regex pattern instead of feed name
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

# Define functions to classify as daily, weekly, or monthly
def is_daily(group):
    weekly_counts = group['timestamp'].dt.isocalendar().week.value_counts()
    return (weekly_counts >= 5).rolling(7).sum().dropna().ge(7).any()

def is_weekly(group):
    weekly_presence = group['timestamp'].dt.isocalendar().week.nunique()
    return weekly_presence >= 9

def is_monthly(group):
    monthly_presence = group['timestamp'].dt.to_period('M').nunique()
    return monthly_presence >= 3

# Classify each name and feed combination
results = []
for (name, feed), group in df_filtered.groupby(['name', 'feed']):
    frequency_type = None
    if is_daily(group):
        frequency_type = 'Daily'
    elif is_weekly(group):
        frequency_type = 'Weekly'
    elif is_monthly(group):
        frequency_type = 'Monthly'
    
    if frequency_type:
        # Extract the time component and convert to minutes since midnight for calculations
        group.loc[:, 'time_in_minutes'] = group['timestamp'].dt.hour * 60 + group['timestamp'].dt.minute
        mean_time_in_minutes = group['time_in_minutes'].mean()
        std_time_in_minutes = group['time_in_minutes'].std()
        
        # Convert mean time back to hours and minutes
        mean_hours = int(mean_time_in_minutes // 60)
        mean_minutes = int(mean_time_in_minutes % 60)
        
        results.append({
            'name': name,
            'feed': feed,
            'frequency': frequency_type,
            'mean_time': f"{mean_hours}:{mean_minutes:02d}",
            'std_deviation_minutes': std_time_in_minutes,
            'timestamps_considered': group['timestamp'].tolist()
        })

# Create DataFrame for results
df_results = pd.DataFrame(results)

# Saving the classified and unclassified data to CSV files
df_results.to_csv('classified_data.csv', index=False)
df_unmatched.to_csv('unclassified_data.csv', index=False)

# Logging completion
logging.info("Data processing complete. Classified and unclassified data saved.")
