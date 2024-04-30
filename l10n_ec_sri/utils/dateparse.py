import datetime
import pytz


def get_date_formats():
    ''' All SRI date formats '''

    date_formats = ['%d%m%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%Y-%m-%d', '%m-%d-%Y',
                    '%d-%m-%Y']
    return date_formats

def get_datetime_formats():
    ''' All SRI datetime formats '''

    date_formats = ['%m/%d/%Y %H:%M:%S %p', '%Y-%m-%d %H:%M:%S %p', '%Y-%m-%d %H:%M:%S',
                    '%m/%d/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z']
    return date_formats

def parse_date(value, date_format=None):
    date_formats = get_date_formats()

    if date_format:
        date_formats.insert(0, date_format)

    _date = None
    for df in date_formats:
        try:
            _date = datetime.datetime.strptime(value, df)
        except ValueError:
            pass
    return _date

def parse_datetime(value, datetime_format=None):
    datetime_formats = get_datetime_formats()
    if datetime_format:
        date_formats.insert(0, datetime_format)

    _date_time = None

    for dtf in datetime_formats:
        try:
            _date_time = datetime.datetime.strptime(value, dtf)
            est = pytz.timezone('US/Pacific')
            _date_time.astimezone(est).replace(tzinfo=None)

        except ValueError:
            pass
    return _date_time.replace(tzinfo=None)

def local_to_i11l_date(value, date_format=None):
    return parse_date(value, date_format)

def local_to_i11l_datetime(value, datetime_format=None):
    return parse_datetime(value, datetime_format)


if __name__ == '__main__':
    print(parse_date('6/19/2021'))
    print(parse_date('01082021'))
    print(parse_date('2021-06-10'))

    print(parse_datetime('6/19/2021 3:48:44 PM'))
    print(parse_datetime('7/29/2021 9:20:09 AM'))
    print(parse_datetime('2021-06-10 1:38:21 am'))
    print(parse_datetime('2021-06-10 12:38:21 pm'))
    print(parse_datetime('2021-06-10 14:38:31'))
    print(parse_datetime('2021-05-27T13:51:56-05:00'))
    print(parse_datetime('2021-05-27T13:51:56-05:00Z'))
