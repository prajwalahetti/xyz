def analyze_daily(df):
    # Ensure timestamp is treated as a datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Group by day and count entries per day
    daily_df = df.groupby(df['timestamp'].dt.date).size().reset_index(name='count')
    
    if len(daily_df) >= 7:
        for i in range(len(daily_df) - 49 + 1):  # Slide through 7-week windows
            window = daily_df.iloc[i:i + 49]  # 7 weeks = 49 days
            
            # Create week column using .loc
            daily_df.loc[:, 'week'] = pd.to_datetime(daily_df['timestamp']).apply(lambda x: x.isocalendar().week)
            
            # Check if there are at least 5 days per week across each of the 7 weeks
            weekly_counts = window.groupby('week')['count'].sum()
            if (weekly_counts >= 5).all():  # At least 5 days per week
                # Calculate mean and std deviation based on hours and minutes
                df.loc[:, 'time_in_minutes'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute
                mean_minutes = df['time_in_minutes'].mean()
                std_minutes = df['time_in_minutes'].std()
                
                # Convert back to hours and minutes
                mean_hours, mean_remaining_minutes = divmod(mean_minutes, 60)
                return "daily", f"{int(mean_hours)}:{int(mean_remaining_minutes):02d}", std_minutes
    return None
