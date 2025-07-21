import logging

def save_outputs(feed_df, rec_df, feed_output_path, rec_output_path):
    feed_df.to_csv(feed_output_path, index=False)
    rec_df.to_csv(rec_output_path, index=False)
    logging.info(f"Saved outputs: {feed_output_path}, {rec_output_path}")
