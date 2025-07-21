import pandas as pd
import re

def rec_sla_report(rec_df, feed_df, mapping_df, rec_frequency_df):
    # Match last feed for each rec_name according to the mapping
    def match_rec(feed_name):
        for _, row in mapping_df.iterrows():
            if re.match(row['feed_pattern'], feed_name):
                return row['rec_name']
        return None
    feed_df['rec_name'] = feed_df['feed_file_name'].apply(match_rec)
    feed_df = feed_df.dropna(subset=['rec_name'])

    # Last feed per rec
    last_feed = (
        feed_df.groupby('rec_name')['feed_received_timestamp']
        .max()
        .reset_index()
        .rename(columns={'feed_received_timestamp': 'last_feed_received_time'})
    )

    # Merge last feed time with recs
    rec_df = rec_df.copy()
    rec_df = rec_df.merge(last_feed, on='rec_name', how='left')
    rec_df['build_delay_minutes'] = (
        rec_df['rec_built_timestamp'] - rec_df['last_feed_received_time']
    ).dt.total_seconds() / 60

    # Compute median, std, frequency per rec
    agg = rec_df.groupby('rec_name')['build_delay_minutes'].agg(['median', 'std']).reset_index()
    agg = agg.rename(columns={
        'median': 'median_build_delay_minutes',
        'std': 'std_dev_build_delay_minutes'
    })
    rec_report = pd.merge(agg, rec_frequency_df, on='rec_name', how='left')
    # rec_built_sea is the most recent timestamp
    latest = rec_df.groupby('rec_name')['rec_built_timestamp'].max().reset_index().rename(columns={'rec_built_timestamp': 'rec_built_sea'})
    rec_report = rec_report.merge(latest, on='rec_name', how='left')

    # Columns per your spec
    rec_report = rec_report[['rec_name', 'rec_built_sea', 'rec_freq', 'median_build_delay_minutes', 'std_dev_build_delay_minutes']]
    return rec_report
