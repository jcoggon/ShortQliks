def user_input_to_icalendar_format(data):
    rrule = ""
    freq = data.get('frequency1')
    if freq:
        rrule = f"RRULE:FREQ={freq}"
        interval = data.get('interval1')
        if interval:
            rrule += f";INTERVAL={interval}"
        if freq == "WEEKLY":
            days = data.getlist('byDay1')
            if days:
                rrule += f";BYDAY={','.join(days)}"
        elif freq in ["MONTHLY", "YEARLY"]:
            # Handle specific rules for monthly and yearly recurrence if needed
            pass
        for unit in ['byHour', 'byMinute', 'bySecond']:
            value = data.get(f'{unit}1')
            if value:
                rrule += f";{unit.upper()}={value}"
    return rrule