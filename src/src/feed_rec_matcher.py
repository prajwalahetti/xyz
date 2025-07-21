import re
import logging

def match_feeds_to_recs(feed_df, mapping_df):
    def get_rec_matches(feed_file):
        matches = []
        for _, row in mapping_df.iterrows():
            try:
                if re.match(row['feed_pattern'], feed_file):
                    matches.append(row['rec_name'])
            except Exception as e:
                logging.error(f"Regex error: {row['feed_pattern']} / {feed_file}: {e}")
        return matches

    feed_df['matched_recs'] = feed_df['feed_file_name'].apply(get_rec_matches)
    feed_df['num_matches'] = feed_df['matched_recs'].apply(len)
    return feed_df

def explode_matched_feeds(feed_df):
    unmatched = feed_df[feed_df['num_matches'] == 0]
    for f in unmatched['feed_file_name'].unique():
        logging.warning(f"Feed {f} did not match any REC pattern.")
    matched_feed_df = feed_df.explode('matched_recs').dropna(subset=['matched_recs']).rename(columns={'matched_recs': 'rec_name'})
    return matched_feed_df
