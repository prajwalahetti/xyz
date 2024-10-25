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
df = pd.read_csv('data.csv')  # Main file in format 'name, feed, timestamp'

# Load name-to-feed mapping file with semicolon-separated regex patterns
logging.info("Loading name-to-feed mapping file with semicolon-separated regex patterns.")
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
                    matched_rows.append(row)  # If there's a match, store the row in matched_rows
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

# Continue with the rest of your analysis...

