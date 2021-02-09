import schedule, time

def schedule_helper(int_weekday, int_freq, str_time, action, **kwargs):
    if int_weekday == 1:
        schedule.every(int_freq).monday.at(str_time).do(action, **kwargs)
    if int_weekday == 2:
        schedule.every(int_freq).tuesday.at(str_time).do(action, **kwargs)
    if int_weekday == 3:
        schedule.every(int_freq).wednesday.at(str_time).do(action, **kwargs)
    if int_weekday == 4:
        schedule.every(int_freq).thursday.at(str_time).do(action, **kwargs)
    if int_weekday == 5:
        schedule.every(int_freq).friday.at(str_time).do(action, **kwargs)
    if int_weekday == 6:
        schedule.every(int_freq).saturday.at(str_time).do(action, **kwargs)
    if int_weekday == 7:
        schedule.every(int_freq).sunday.at(str_time).do(action, **kwargs)

    return None
