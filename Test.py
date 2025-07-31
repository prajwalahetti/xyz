import pandas as pd
from dateutil import parser
from typing import Optional
import re

# === CONFIGURATION ===
INPUT_CSV = "input.csv"                     # CSV file with a 'timestamp' column
OUTPUT_CSV = "parsed_output.csv"            # Output CSV file with parsed datetimes
UNMATCHED_LOG_FILE = "unmatched_timestamps.txt"  # File to log failed entries
TIMESTAMP_COLUMN = "timestamp"              # Name of the timestamp column


# === Globals ===
unmatched_entries = []


# === Timestamp Parsing Function ===
def parse_timestamp_to_utc(text: Optional[str]) -> Optional[pd.Timestamp]:
    """
    Parse a messy timestamp string into a UTC datetime.
    Handles formats like:
      - 31 July 2025 01:23:45.678 PM GMT
      - 02 Dec 2024 11:59:59.123 AM +1:00
      - ISO 8601 formats with or without timezone
    Returns pd.Timestamp in UTC, or NaT if it fails.
    """
    try:
        if pd.isna(text) or not str(text).strip():
            raise ValueError("Empty or null")

        text = str(text).strip()

        # Normalize known timezone keywords
        text = re.sub(r'\bGMT\b', '+0000', text, flags=re.IGNORECASE)

        # Parse using dateutil
        dt = parser.parse(text)

        # Convert to UTC
        return dt.astimezone(tz=None).astimezone(tz=pd.Timestamp.utcnow().tz)

    except Exception as e:
        unmatched_entries.append(text)
        return pd.NaT


# === Main Script ===
def main():
    print(f"📥 Reading from {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)

    if TIMESTAMP_COLUMN not in df.columns:
        raise ValueError(f"Column '{TIMESTAMP_COLUMN}' not found in input CSV.")

    # Parse timestamps
    print("🧠 Parsing timestamps...")
    df["parsed_timestamp"] = df[TIMESTAMP_COLUMN].apply(parse_timestamp_to_utc)

    # Format parsed timestamp for readability
    df["parsed_timestamp"] = df["parsed_timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Save output CSV
    print(f"💾 Writing parsed data to {OUTPUT_CSV}")
    df.to_csv(OUTPUT_CSV, index=False)

    # Save unmatched log
    if unmatched_entries:
        print(f"⚠️ {len(unmatched_entries)} entries could not be parsed. Logging to {UNMATCHED_LOG_FILE}")
        with open(UNMATCHED_LOG_FILE, "w") as f:
            f.write("Unmatched timestamp entries:\n\n")
            for entry in unmatched_entries:
                f.write(f"{repr(entry)}\n")
    else:
        print("✅ All timestamps parsed successfully.")


if __name__ == "__main__":
    main()
