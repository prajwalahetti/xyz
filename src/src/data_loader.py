import pandas as pd

def load_data(rec_path, feed_path, mapping_path):
    rec_df = pd.read_csv(rec_path)
    feed_df = pd.read_csv(feed_path)
    map_df = pd.read_csv(mapping_path)
    rec_df['rec_built_timestamp'] = pd.to_datetime(rec_df['rec_built_timestamp'])
    feed_df['feed_received_timestamp'] = pd.to_datetime(feed_df['feed_received_timestamp'])
    return rec_df, feed_df, map_df
