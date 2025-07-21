import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Ensure output folder exists
os.makedirs('data', exist_ok=True)

# Seed for reproducibility
random.seed(42)

def generate_random_rec_names(n):
    prefixes = ['RPT', 'DAT', 'SYN', 'TRX', 'LOG']
    return [f"{random.choice(prefixes)}_{i+1:03}" for i in range(n)]

def generate_feed_name(rec_name, date, variant=None):
    base = rec_name.replace('RPT', 'feed')
    suffix = date.strftime('%Y%m%d')
    if variant:
        return f"{base}_{suffix}_v{variant}.csv"
    return f"{base}_{suffix}.csv"

# ---------- Generate REC Build Data ----------
rec_rows = []
rec_feed_map = []
feed_rows = []

NUM_RECS = 5
rec_names = generate_random_rec_names(NUM_RECS)

for rec in rec_names:
    pattern_choice = random.choice(['daily', 'weekly', 'monthly'])
    base_day = datetime(2025, 6, 1) + timedelta(days=random.randint(0, 30))
    
    if pattern_choice == 'daily':
        for i in range(5):
            day = base_day + timedelta(days=i)
            rec_rows.append([rec, (day + timedelta(hours=10 + random.randint(0, 2))).strftime('%Y-%m-%d %H:%M:%S')])

            # 2 feeds per day
            for v in [1, 2]:
                feed_time = (day + timedelta(hours=8 + v, minutes=random.randint(0, 10)))
                feed_name = generate_feed_name(rec, day, variant=v)
                feed_rows.append([feed_name, feed_time.strftime('%Y-%m-%d %H:%M:%S')])

    elif pattern_choice == 'weekly':
        for week in range(4):
            day = base_day + timedelta(weeks=week)
            rec_rows.append([rec, (day + timedelta(hours=10)).strftime('%Y-%m-%d %H:%M:%S')])

            # 1 feed per week
            feed_time = (day + timedelta(hours=8, minutes=random.randint(0, 30)))
            feed_name = generate_feed_name(rec, day)
            feed_rows.append([feed_name, feed_time.strftime('%Y-%m-%d %H:%M:%S')])
    
    elif pattern_choice == 'monthly':
        for month_add in range(3):
            day = (base_day + timedelta(days=month_add * 30))
            rec_rows.append([rec, (day + timedelta(hours=11)).strftime('%Y-%m-%d %H:%M:%S')])

            feed_time = (day + timedelta(hours=7, minutes=random.randint(0, 45)))
            feed_name = generate_feed_name(rec, day)
            feed_rows.append([feed_name, feed_time.strftime('%Y-%m-%d %H:%M:%S')])

    # Map feed pattern to rec
    rec_id = rec
    rec_prefix = rec_id.replace("RPT", "feed")
    rec_feed_map.append([rec_id, f"^{rec_prefix}_.*\\.csv$"])

# ---------- Save rec_build_sla.csv ----------
df_rec = pd.DataFrame(rec_rows, columns=['rec_name', 'rec_built_timestamp'])
df_rec.to_csv('data/rec_build_sla.csv', index=False)

# ---------- Save feed_sla.csv ----------
df_feed = pd.DataFrame(feed_rows, columns=['feed_file_name', 'feed_received_timestamp'])
df_feed.to_csv('data/feed_sla.csv', index=False)

# ---------- Save rec_feed_mapping.csv ----------
df_map = pd.DataFrame(rec_feed_map, columns=['rec_name', 'feed_pattern'])
df_map.to_csv('data/rec_feed_mapping.csv', index=False)

print("✅ Random sample data generated in ./data/")
print("- rec_build_sla.csv")
print("- feed_sla.csv")
print("- rec_feed_mapping.csv")
