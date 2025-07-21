import pandas as pd

def load_data(rec_path, feed_path, mapping_path):
    rec_build_df = pd.read_csv(rec_path)
    feed_df = pd.read_csv(feed_path)
    mapping_df = pd.read_csv(mapping_path)
    rec_build_df['rec_built_timestamp'] = pd.to_datetime(rec_build_df['rec_built_timestamp'], errors='coerce')
    feed_df['feed_received_timestamp'] = pd.to_datetime(feed_df['feed_received_timestamp'], errors='coerce')
    return rec_build_df, feed_df, mapping_df
