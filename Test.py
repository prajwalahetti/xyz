import pandas as pd
import re

# Sample input
df = pd.DataFrame({'timestamp': [
    '2025-07-31 14:00:00 PST',
    '31/07/2025 22:00 +0530',
    'Jul 31, 2025 04:00PM UTC',
    '07/31/2025 02:00 PM EDT',
    '2025-07-31T18:00:00Z',
    'Logged at: 2025-07-31 13:00:00 UTC',
    'nonsense string',
    '',
    None
]})

# List to collect unmatched/bad values
unmatched_entries = []

# Function to extract parts from string
def extract_parts_or_log(text):
    text = str(text).strip() if text else ''
    
    # Regex pattern with named groups
    pattern = (
        r'(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'            # 07/31/2025 or 31-07-2025
        r'\d{4}[/-]\d{2}[/-]\d{2}|'                           # 2025-07-31
        r'[A-Za-z]{3} \d{1,2}, \d{4})'                        # Jul 31, 2025
        r'\s*'
        r'(?P<time>\d{1,2}:\d{2}(?::\d{2})?)?'                # HH:MM[:SS]
        r'\s*'
        r'(?P<ampm>[APap][Mm])?'                              # AM/PM
        r'\s*'
        r'(?P<offset>[+-]\d{2}:?\d{2}|Z)?'                    # +0530 or Z
        r'\s*'
        r'(?P<tz>[A-Z]{2,4})?'                                # Timezone like UTC, PST, EDT
    )
    
    match = re.search(pattern, text)
    
    if match:
        return pd.Series({
            'date': match.group('date'),
            'time': match.group('time'),
            'ampm': match.group('ampm'),
            'offset': match.group('offset'),
            'timezone': match.group('tz')
        })
    else:
        unmatched_entries.append(text)
        return pd.Series({
            'date': None,
            'time': None,
            'ampm': None,
            'offset': None,
            'timezone': None
        })

# Apply to the DataFrame
extracted = df['timestamp'].apply(extract_parts_or_log)
df = df.join(extracted)

# Show unmatched entries
print("\n❌ Unmatched entries:")
for bad in unmatched_entries:
    print(f" - {repr(bad)}")

# Display result
print("\n✅ Parsed DataFrame:")
print(df)
