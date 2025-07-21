import re

def match_feeds_to_recs(feed_df, mapping_df):
    def find_rec_name(feed_file):
        for _, row in mapping_df.iterrows():
            if re.match(row['feed_pattern'], feed_file):
                return row['rec_name']
        return None
    feed_df['rec_name'] = feed_df['feed_file_name'].apply(find_rec_name)
    feed_df = feed_df.dropna(subset=['rec_name'])
    return feed_df
