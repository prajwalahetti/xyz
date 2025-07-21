import logging
from config_loader import load_config
from data_loader import load_data
from feed_rec_matcher import match_feeds_to_recs, explode_matched_feeds
from frequency_analysis import assign_feed_frequencies, assign_rec_frequencies
from sla_check import calculate_rec_sla, calculate_feed_sla
from output_writer import save_outputs

def setup_logging(logfile='analysis_logs.log'):
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )

def main():
    setup_logging()
    config = load_config('frequency_config.yaml')
    rec_build_df, feed_df, mapping_df = load_data(
        'rec_build_sla.csv', 'feed_sla.csv', 'rec_feed_mapping.csv'
    )
    feed_df = match_feeds_to_recs(feed_df, mapping_df)
    matched_feed_df = explode_matched_feeds(feed_df)
    matched_feed_df = assign_feed_frequencies(matched_feed_df, config)
    rec_build_df = assign_rec_frequencies(rec_build_df, config)
    rec_sla = calculate_rec_sla(rec_build_df, matched_feed_df)
    matched_feed_df = calculate_feed_sla(matched_feed_df)

    feed_sla_percent = matched_feed_df['feed_on_time'].mean() * 100
    rec_sla_percent = rec_sla['rec_met_sla'].mean() * 100
    logging.info(f"Feed SLA met: {feed_sla_percent:.2f}%")
    logging.info(f"REC SLA met: {rec_sla_percent:.2f}%")
    print(f"Feed SLA: {feed_sla_percent:.2f}% | REC SLA: {rec_sla_percent:.2f}%")
    print("Frequency classifications and SLA status saved to CSV and logs.")

    save_outputs(matched_feed_df, rec_sla, 'feed_sla_output.csv', 'rec_sla_output.csv')

if __name__ == "__main__":
    main()
