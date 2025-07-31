import pandas as pd
from dateutil import parser
from typing import Optional
import re
from datetime import datetime

# === CONFIGURATION ===
INPUT_CSV = "input.csv"
OUTPUT_CSV = "parsed_output.csv"
UNMATCHED_LOG_FILE = "unmatched_timestamps.txt"
TIMESTAMP_COLUMN = "timestamp"

unmatched_entries = []

def normalize_timestamp(text: str) -> str:
    """
    Clean and normalize the timestamp string to improve parseability.
    Handles:
      - "GMT" -> "+0000"
      - Remove unwanted prefixes/suffixes
      - Collapse multiple spaces
    """
    text = text.strip()
    text = re.sub(r"\bGMT\b", "+0000", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text


def parse_timestamp_to_utc(text: Optional[str]) -> Optional[pd.Timestamp]:
    try:
        if pd.isna(text) or not str(text).strip():
            raise ValueError("Empty or null")

        text = str(text).strip()

        # === CUSTOM HANDLER ===
        # Format: 21-MAR-25 2.07.06.4343 AM
        custom_match = re.match(
            r"(\d{1,2})-([A-Z]{3})-(\d{2}) (\d{1,2})\.(\d{2})\.(\d{2})\.(\d{1,6}) (AM|PM)",
            text,
            flags=re.IGNORECASE
        )

        if custom_match:
            day, month_abbr, year_2digit, hour, minute, second, ms, meridian = custom_match.groups()

            # Convert to full year (assumes 2000s)
            year = int(year_2digit)
            year += 2000 if year < 50 else 1900

            # Standardize casing
            month_abbr = month_abbr.capitalize()

            dt_str = f"{day}-{month_abbr}-{year} {hour}:{minute}:{second}.{ms} {meridian.upper()}"
            dt_obj = datetime.strptime(dt_str, "%d-%b-%Y %I:%M:%S.%f %p")

            return pd.Timestamp(dt_obj).tz_localize("UTC")

        # === FALLBACK ===
        clean_text = normalize_timestamp(text)
        dt = parser.parse(clean_text)
        return dt.astimezone(tz=None).astimezone(tz=pd.Timestamp.utcnow().tz)

    except Exception as e:
        unmatched_entries.append(f"{text} | Error: {e}")
        return pd.NaT


def main():
    print(f"📥 Reading from {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)

    if TIMESTAMP_COLUMN not in df.columns:
        raise ValueError(f"Column '{TIMESTAMP_COLUMN}' not found in input CSV.")

    print("🧠 Parsing timestamps...")
    df["parsed_timestamp"] = df[TIMESTAMP_COLUMN].apply(parse_timestamp_to_utc)

    # Optional: format output
    df["parsed_timestamp"] = df["parsed_timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    print(f"💾 Writing parsed data to {OUTPUT_CSV}")
    df.to_csv(OUTPUT_CSV, index=False)

    if unmatched_entries:
        print(f"⚠️ {len(unmatched_entries)} entries could not be parsed. Logging to {UNMATCHED_LOG_FILE}")
        with open(UNMATCHED_LOG_FILE, "w") as f:
            f.write("Unmatched timestamp entries with error messages:\n\n")
            for entry in unmatched_entries:
                f.write(f"{entry}\n")
    else:
        print("✅ All timestamps parsed successfully.")


if __name__ == "__main__":
    main()
