from gestor_absencies.models import Worker
import dateutil

def jwt_response_token_user_id(token, user=None, request=None):
	user = Worker.objects.filter(username=request.data['username']).first()
	return {
		'user_id': user.id,
		'is_admin': user.is_superuser,
		'token': token,
	}


def computable_days_between_dates(start_time, end_time, dates_types):
    return len(list(dateutil.rrule.rrule(
        dtstart=start_time,
        until=end_time,
        freq=dateutil.rrule.DAILY,
        byweekday=dates_types
    )))

def find_concurrence_dates(o1, o2):	# TODO with interval
    if o1.start_time > o2.start_time and o1.start_time < o2.end_time:
        return o1.start_time, o2.end_time
    if o2.start_time > o1.start_time and o2.start_time < o1.end_time:
        return o2.start_time, o1.end_time
    if o1.end_time > o2.start_time and o1.end_time < o2.end_time:
        return o2.start_time, o1.end_time
    if o2.end_time > o1.start_time and o2.end_time < o1.end_time:
        return o2.start_time, o2.end_time
    if o1.start_time < o2.start_time and o1.end_time > o2.end_time:
        return o2.start_time, o2.end_time
    if o1.start_time > o2.start_time and o1.end_time > o2.end_time:
        return o1.start_time, o1.end_time
    return o1.start_time, o1.end_time

def between_dates(start_interval, end_interval, date):
	return start_interval < date and end_interval > date
