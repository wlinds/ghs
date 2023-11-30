import datetime

def humanize_time(time_elapsed):
    days, seconds = divmod(time_elapsed.total_seconds(), 24 * 3600)
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        if days == 1:
            return f"{int(days)} day ago"
        else:
            return f"{int(days)} days ago"
    elif hours > 0:
        if hours == 1:
            return f"{int(hours)} hour ago"
        else:
            return f"{int(hours)} hours ago"
    elif minutes > 0:
        if minutes == 1:
            return f"{int(minutes)} minute ago"
        else:
            return f"{int(minutes)} minutes ago"
    else:
        return "Just now"