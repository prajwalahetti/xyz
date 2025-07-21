def write_rec_sla_report(df, filename):
    df.to_csv(filename, index=False)
    print(f"✅ rec_sla_report written to {filename}")

def write_feed_frequency_report(df, filename):
    df.to_csv(filename, index=False)
    print(f"✅ feed_frequency_report written to {filename}")
