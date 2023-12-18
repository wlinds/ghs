import pandas as pd

# Standalone functions are initially a good idea, but for performance should probably refactor all into a class

def get_nightowl_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    nightowl_stat = df[(df['hour'] >= 22) | (df['hour'] <= 6)]['user'].value_counts().idxmax()
    val = df[(df['hour'] >= 22) | (df['hour'] <= 6)]['user'].value_counts().max()

    return nightowl_stat, val

def get_early_bird_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    early_bird_stat = df[(df['hour'] >= 6) & (df['hour'] <= 10)]['user'].value_counts().idxmax()
    val = df[(df['hour'] >= 6) & (df['hour'] <= 10)]['user'].value_counts().max()

    return early_bird_stat, val

def get_weekend_warrior_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['day_of_week'] = df['datetime'].dt.dayofweek
    weekend_warrior_user = (
            df[df['day_of_week'].isin([5, 6])]
            .groupby('user')
            .size()
            .idxmax()
        )

    val = (
        df[df['day_of_week'].isin([5, 6])]
        .groupby('user')
        .size()
        .max()
    )

    return weekend_warrior_user, val

def get_chatty_coder_stat(df):
    df['commit_message_length'] = df['commit_message'].apply(len)
    chatty_coder_stats = df.groupby('user')['commit_message_length'].mean()
    chatty_coder_user = chatty_coder_stats.idxmax()
    val = chatty_coder_stats.max().round(2)

    return chatty_coder_user, val

def get_no_time_for_that_stat(df):
    df['commit_message_length'] = df['commit_message'].apply(len)
    no_time_for_that_stats = df.groupby('user')['commit_message_length'].mean()
    no_time_for_that_user = no_time_for_that_stats.idxmin()
    val = no_time_for_that_stats.min()

    return no_time_for_that_user, val.round()


def get_speed_demon_stat(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = df['datetime'].dt.date
    commits_per_day_stats = df.groupby(['user', 'date']).size().reset_index(name='commits_per_day')
    commits_per_day_stats = commits_per_day_stats[commits_per_day_stats['commits_per_day'] > 0]
    avg_commits_per_day_stats = commits_per_day_stats.groupby('user')['commits_per_day'].mean()
    speed_demon_user = avg_commits_per_day_stats.idxmax()
    val = avg_commits_per_day_stats.max()

    return speed_demon_user, val


stat_configs = [
    {"title": "Nightowl", "desc": "Most commits during night", "stat_function": get_nightowl_stat, "icon": "🦉", "suffix": "commits made 22:00 - 6:00 "},
    {"title": "Early Bird", "desc": "Most early morning commits", "stat_function": get_early_bird_stat, "icon": "🌞", "suffix": "commits made 06:00 - 10:00"},
    {"title": "Weekend Warrior", "desc": "Most commits during weekends", "stat_function": get_weekend_warrior_stat, "icon": "🤓", "suffix": "commits during weekends"},
    {"title": "Chatty Coder", "desc": "Longest commit messages", "stat_function": get_chatty_coder_stat, "icon": "🗣️", "suffix": "characters in average commit message"},
    {"title": "No Time For That", "desc": "Shortest commit messages", "stat_function": get_no_time_for_that_stat, "icon": "💨", "suffix": "characters in average commit message"},
    {"title": "Speed Demon", "desc": "Highest average commits per day", "stat_function": get_speed_demon_stat, "icon": "😈", "suffix": "commits per day in average"},
]
