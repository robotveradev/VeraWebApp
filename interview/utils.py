from datetime import timedelta


def get_recruiter_for_time(recruiters, date_time, duration):
    if not recruiters.exists():
        return None
    for recruiter in recruiters:
        busy = \
            recruiter.recruiter_scheduled_meetings.filter(date__gte=date_time.date(),
                                                          date__lt=date_time.date() + timedelta(days=1),
                                                          time__gt=(date_time - timedelta(minutes=duration)).time(),
                                                          time__lt=(date_time + timedelta(minutes=duration)).time())
        if not busy.exists():
            return recruiter


def get_first_available_time(times, duration):
    for i in range(len(times) - 1):
        if times[i] + timedelta(minutes=duration) < times[i + 1]:
            return times[i] + timedelta(minutes=duration)
    return times[-1] + timedelta(minutes=duration)
