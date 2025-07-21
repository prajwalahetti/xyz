def detect_frequency_simple(group, ts_col, config):
    df = group.sort_values(ts_col)
    df['date'] = df[ts_col].dt.date

    # Daily
    daily_params = config.get('daily', {})
    min_daily_occ = daily_params.get('min_daily_occurrences', 2)
    streak_days = daily_params.get('streak_days', 5)
    count_per_day = df.groupby('date').size()
    daily_flag = False
    if len(count_per_day) >= streak_days:
        flags = (count_per_day >= min_daily_occ).astype(int)
        if flags.rolling(streak_days, min_periods=streak_days).sum().max() == streak_days:
            daily_flag = True

    # Weekly
    weekly_params = config.get('weekly', {})
    weekly_occ = weekly_params.get('weekly_occurrences', 1)
    streak_weeks = weekly_params.get('streak_weeks', 4)
    df['week'] = df[ts_col].dt.isocalendar().week
    df['year'] = df[ts_col].dt.isocalendar().year
    count_per_week = df.groupby(['year','week']).size()
    weekly_flag = False
    if len(count_per_week) >= streak_weeks:
        flags = (count_per_week == weekly_occ).astype(int)
        if flags.rolling(streak_weeks, min_periods=streak_weeks).sum().max() == streak_weeks:
            weekly_flag = True

    if daily_flag:
        return 'daily'
    elif weekly_flag:
        return 'weekly'
    return 'irregular'

def assign_feed_frequencies(feed_df, config):
    feed_freqs = (
        feed_df.groupby(['feed_file_name', 'rec_name'])
        .apply(lambda g: detect_frequency_simple(g, 'feed_received_timestamp', config))
        .reset_index()
        .rename(columns={0: 'feed_actual_frequency'})
    )
    return feed_df.merge(feed_freqs, on=['feed_file_name', 'rec_name'], how='left')

def assign_rec_frequencies(rec_build_df, config):
    rec_freqs = (
        rec_build_df.groupby('rec_name')
        .apply(lambda g: detect_frequency_simple(g, 'rec_built_timestamp', config))
        .reset_index()
        .rename(columns={0: 'rec_actual_frequency'})
    )
    return rec_build_df.merge(rec_freqs, on='rec_name', how='left')
