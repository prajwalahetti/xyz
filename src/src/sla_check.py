from datetime import timedelta
import logging

def calculate_rec_sla(rec_build_df, matched_feed_df, sla_hours=6):
    last_feed = (
        matched_feed_df.groupby('rec_name')['feed_received_timestamp']
        .max()
        .reset_index()
        .rename(columns={'feed_received_timestamp': 'last_feed_time'})
    )
    rec_sla = rec_build_df.merge(last_feed, on='rec_name', how='left')
    rec_sla['rec_met_sla'] = (
        (rec_sla['rec_built_timestamp'] >= rec_sla['last_feed_time']) &
        (rec_sla['rec_built_timestamp'] <= rec_sla['last_feed_time'] + timedelta(hours=sla_hours))
    )
    rec_sla['rec_met_sla'] = rec_sla['rec_met_sla'].fillna(False)
    missing_feed_recs = rec_sla[rec_sla['last_feed_time'].isnull()]
    for rec in missing_feed_recs['rec_name']:
        logging.warning(f"REC {rec} has no related feed arrivals.")
    return rec_sla

def calculate_feed_sla(matched_feed_df):
    matched_feed_df['feed_on_time'] = True  # Placeholder
    return matched_feed_df
