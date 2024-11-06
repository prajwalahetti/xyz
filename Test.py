def analyze_daily(df):
    # Ensure timestamp is treated as a datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Group by day and count entries per day
    daily_df = df.groupby(df['timestamp'].dt.date).size().reset_index(name='count')
    daily_df.columns = ['timestamp', 'count']  # Rename for clarity

    # Add 'week' column to daily_df directly, based on the ISO calendar week of each date
    daily_df['week'] = pd.to_datetime(daily_df['timestamp']).apply(lambda x: x.isocalendar().week)

    if len(daily_df) >= 7:
        # Slide through possible 7-week windows within daily_df
        for i in range(len(daily_df) - 49 + 1):  # 7 weeks = 49 days
            window = daily_df.iloc[i:i + 49]  # Select a 7-week window
            
            # Group by 'week' within this window and check if there are at least 5 entries per week
            weekly_counts = window.groupby('week')['count'].sum()
            if (weekly_counts >= 5).all():  # Require at least 5 entries per week in all 7 weeks
                # Calculate mean and std deviation in hours and minutes
                df['time_in_minutes'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
                mean_minutes = df['time_in_minutes'].mean()
                std_minutes = df['time_in_minutes'].std()

                # Convert back to hours and minutes for better readability
                mean_hours, mean_remaining_minutes = divmod(mean_minutes, 60)
                return "daily", f"{int(mean_hours)}:{int(mean_remaining_minutes):02d}", std_minutes
    return None
