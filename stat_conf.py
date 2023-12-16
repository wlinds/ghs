import pandas as pd

# Standalone functions are initially a good idea, but for performance should probably refactor all into a class

def get_nightowl_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    return df[(df['hour'] >= 22) | (df['hour'] <= 6)]['user'].value_counts().idxmax()

def get_early_bird_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    return df[(df['hour'] >= 6) & (df['hour'] <= 10)]['user'].value_counts().idxmax()

def get_code_marathoner_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['commit_diff'] = df.groupby('user')['datetime'].diff().dt.total_seconds()
    marathoner_user = df.groupby('user')['commit_diff'].idxmax()
    return df.loc[marathoner_user, 'user'].values[0]

def get_weekend_warrior_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day_of_week'] = df['datetime'].dt.dayofweek
    ww_user = df[df['day_of_week'].isin([5, 6])].groupby('user').size().idxmax()
    return ww_user

def get_chatty_coder_stat(df):
    df['commit_message_length'] = df['commit_message'].apply(len)
    cc_user = df.groupby('user')['commit_message_length'].idxmax()
    return df.loc[cc_user, 'user'].values[0]

def get_no_time_for_that_stat(df):
    df['commit_message_length'] = df['commit_message'].apply(len)
    no_time_for_that = df['commit_message_length'].idxmin()
    return df.loc[no_time_for_that, 'user']

def get_speed_demon_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['commit_diff'] = df.groupby('user')['datetime'].diff().dt.total_seconds()
    sd_user = df.groupby('user')['commit_diff'].mean().idxmin()
    return sd_user

stat_configs = [
    {"title": "Nightowl", "desc": "Most commits during night", "stat_function": get_nightowl_stat, "icon": "🦉"},
    {"title": "Early Bird", "desc": "Most early morning commits", "stat_function": get_early_bird_stat, "icon": "🌞"},
    {"title": "Code Marathoner", "desc": "Longest continuous coding streak", "stat_function": get_code_marathoner_stat, "icon": "🏃"},
    {"title": "Weekend Warrior", "desc": "Most commits during weekends", "stat_function": get_weekend_warrior_stat, "icon": "🤓"},
    {"title": "Chatty Coder", "desc": "Longest commit messages", "stat_function": get_chatty_coder_stat, "icon": "🗣️"},
    {"title": "No Time For That", "desc": "Shortest commit messages", "stat_function": get_no_time_for_that_stat, "icon": "💨"},
    {"title": "Speed Demon", "desc": "Highest average commits per day", "stat_function": get_speed_demon_stat, "icon": "😈"},
]