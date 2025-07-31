import pandas as pd
from datetime import timedelta

# Load and parse data
df = pd.read_csv("arrival_data.csv", usecols=["b", "c"], parse_dates=["c"])
df.columns = ["name", "timestamp"]

# Convert to UTC (GMT)
df["timestamp"] = df["timestamp"].dt.tz_convert("UTC") if df["timestamp"].dt.tz else df["timestamp"].dt.tz_localize(None).dt.tz_localize("UTC")

# Extract date parts
df["date"] = df["timestamp"].dt.date
df["week"] = df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time.date())
df["month"] = df["timestamp"].dt.to_period("M").apply(lambda r: r.start_time.date())

# --- SLA CALCULATION ---
df = df.sort_values(by=["name", "timestamp"])
df["sla_minutes"] = df.groupby("name")["timestamp"].diff().dt.total_seconds() / 60
df = df.dropna(subset=["sla_minutes"])

sla_stats = df.groupby("name")["sla_minutes"].agg(["median", "std"]).reset_index()

# Convert to hh:mm format
def format_hm(minutes):
    if pd.isna(minutes):
        return "N/A"
    h = int(minutes // 60)
    m = int(round(minutes % 60))
    return f"{h}h {m:02d}m"

sla_stats["median_sla"] = sla_stats["median"].apply(format_hm)
sla_stats["std_sla"] = sla_stats["std"].apply(format_hm)
sla_stats = sla_stats[["name", "median_sla", "std_sla"]]

# --- FREQUENCY CLASSIFICATION ---
results = []

def has_consecutive_streak(periods, required, threshold_func):
    periods = sorted(periods)
    streak = 0
    for i in range(len(periods) - required + 1):
        window = periods[i:i+required]
        expected = [window[0] + timedelta(weeks=j) for j in range(required)]
        if window == expected and all(threshold_func(p) for p in window):
            return True
    return False

for name, group in df.groupby("name"):
    week_counts = group.groupby("week")["date"].nunique()
    month_counts = group.groupby("month")["date"].nunique()
    
    # Daily: 5 days/week for 7 consecutive weeks
    if has_consecutive_streak(week_counts.index.tolist(), 7, lambda w: week_counts[w] >= 5):
        freq = "daily"
    
    # Weekly: once/week for 7 consecutive weeks
    elif has_consecutive_streak(week_counts.index.tolist(), 7, lambda w: week_counts[w] >= 1):
        freq = "weekly"
    
    # Monthly: once/month for 3 consecutive months
    else:
        month_list = sorted(month_counts.index.tolist())
        found = False
        for i in range(len(month_list) - 2):
            m0 = month_list[i]
            m1 = month_list[i+1]
            m2 = month_list[i+2]
            if (
                (m1.month - m0.month == 1 or (m0.month == 12 and m1.month == 1)) and
                (m2.month - m1.month == 1 or (m1.month == 12 and m2.month == 1)) and
                all(month_counts.get(m, 0) >= 1 for m in [m0, m1, m2])
            ):
                freq = "monthly"
                found = True
                break
        if not found:
            freq = "unclassified"

    results.append((name, freq))

freq_df = pd.DataFrame(results, columns=["name", "frequency"])

# --- COMBINE AND EXPORT ---
final_df = pd.merge(sla_stats, freq_df, on="name", how="outer").fillna("unclassified")
final_df.to_csv("combined_sla_frequency_analysis.csv", index=False)
print("Saved to combined_sla_frequency_analysis.csv")
