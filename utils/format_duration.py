def format_duration(minutes):
    minutes = int(round(minutes))
    if minutes < 60:
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit}"

    hours = minutes // 60
    mins = minutes % 60

    if hours < 24:
        hour_unit = "hr" if hours == 1 else "hrs"
        min_unit = "minute" if mins == 1 else "minutes"
        return f"{hours} {hour_unit} {mins} {min_unit}"

    days = hours // 24
    hrs = hours % 24

    day_unit = "day" if days == 1 else "days"
    hr_unit = "hr" if hrs == 1 else "hrs"
    min_unit = "minute" if mins == 1 else "minutes"

    parts = []

    if days > 0:
        parts.append(f"{days} {day_unit}")
    if hrs > 0:
        parts.append(f"{hrs} {hr_unit}")
    if mins > 0:
        parts.append(f"{mins} {min_unit}")

    return " ".join(parts)
    
    
    