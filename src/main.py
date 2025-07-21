from src.data_loader import load_data
from src.feed_rec_matcher import match_feeds_to_recs
from src.frequency_analysis import (
    calculate_rec_frequency,
    calculate_feed_frequency_by_mapping
)
from src.sla_check import rec_sla_report
from src.output_writer import (
    write_rec_sla_report,
    write_feed_frequency_report
)

def main():
    rec_df, feed_df, map_df = load_data(
        'data/rec_build_sla.csv', 'data/feed_sla.csv', 'data/rec_feed_mapping.csv'
    )
    feed_df = match_feeds_to_recs(feed_df, map_df)
    rec_frequency_df = calculate_rec_frequency(rec_df)
    rec_report = rec_sla_report(rec_df, feed_df, map_df, rec_frequency_df)
    write_rec_sla_report(rec_report, 'data/rec_sla_report.csv')

    feed_freq_report = calculate_feed_frequency_by_mapping(feed_df, map_df)
    write_feed_frequency_report(feed_freq_report, 'data/feed_frequency_report.csv')

    print("✅ All reports generated in /data.")

if __name__ == "__main__":
    main()
