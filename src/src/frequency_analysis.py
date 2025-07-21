import pandas as pd
import re

def calculate_rec_frequency(rec_df):
    def classify_frequency(times):
        times = sorted(times)
        if len(times) < 2:
            return 'irregular'
        days = pd.Series([t.date() for t in times])
        counts_per_day = days.value_counts().sort_index()
        daily_streak = 0
        for cnt in counts_per_day:
            daily_streak = daily_streak + 1 if cnt > 1 else 0
            if daily_streak >= 5:
                return 'daily'
        weeks = pd.Series([t.isocalendar()[1] for t in times])
        counts_per_week = weeks.value_counts().sort_index()
        weekly_streak = 0
        expected_week = None
        for week_num in sorted(counts_per_week.index):
            if counts_per_week[week_num] == 1:
                if expected_week is None or week_num == expected_week:
                    weekly_streak += 1
                    expected_week = week_num + 1
                else:
                    weekly_streak = 1
                    expected_week = week_num + 1
            else:
                weekly_streak = 0
                expected_week = week_num + 1
            if weekly_streak >= 4:
                return 'weekly'
        months = pd.Series([(t.year, t.month) for t in times])
        months_unique = months.drop_duplicates()
        if len(months_unique) >= 3:
            return 'monthly'
        return 'irregular'
    rec_df = rec_df.copy()
    rec_df['rec_built_timestamp'] = pd.to_datetime(rec_df['rec_built_timestamp'])
    freq_list = rec_df.groupby('rec_name')['rec_built_timestamp'].apply(classify_frequency).reset_index()
    freq_list = freq_list.rename(columns={'rec_built_timestamp': 'rec_freq'})
    return freq_list

def calculate_feed_frequency_by_mapping(feed_df, mapping_df):
    results = []
    for _, map_row in mapping_df.iterrows():
        rec_name = map_row['rec_name']
        pattern = map_row['feed_pattern']
        mask = feed_df['feed_file_name'].apply(lambda fn: bool(re.match(pattern, fn)))
        arrivals = feed_df.loc[mask, 'feed_received_timestamp'].sort_values()
        intervals = arrivals.diff().dropna().dt.total_seconds() / 60  # in minutes

        if len(intervals) == 0:
            median = None
            stddev = None
            freq = 'irregular'
        else:
            median = round(intervals.median(), 2)
            stddev = round(intervals.std(), 2) if len(intervals) > 1 else 0
            if 20*60 <= median <= 28*60:
                freq = 'daily'
            elif 6*24*60 <= median <= 8*24*60:
                freq = 'weekly'
            elif 28*24*60 <= median <= 31*24*60:
                freq = 'monthly'
            else:
                freq = 'irregular'
        results.append({
            'rec_name': rec_name,
            'feed_pattern': pattern,
            'frequency': freq,
            'median_arrival_interval_minutes': median,
            'std_dev_arrival_interval_minutes': stddev
        })
    return pd.DataFrame(results)
