def ensure_full_datetime_format(dt_str):
    """Ensure the datetime string is in the format 'YYYY-MM-DDTHH:MM:SS'."""
    if len(dt_str) == 13:  # Format is 'YYYY-MM-DDTHH'
        return dt_str + ":00:00"
    elif len(dt_str) == 16:  # Format is 'YYYY-MM-DDTHH:MM'
        return dt_str + ":00"
    return dt_str