
def calculate_datetime(dt, morning, afternoon, is_start):
    if is_start:
        if morning:
            date = dt.replace(hour=9, minute=0, second=0)
        else:
            date = dt.replace(hour=13, minute=0, second=0)     # Refactor
    else:
        if afternoon:
            date = dt.replace(hour=17, minute=0, second=0)
        else:
            date = dt.replace(hour=13, minute=0, second=0)     # Refactor
    
    return date
