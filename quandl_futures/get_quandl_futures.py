import quandl
import configparser
import datetime as dt

def get_brent_cme_forward(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    month_array = []
    last_settle = []
    start_date = dt.datetime.now() - dt.timedelta(days=3)
    start_date = start_date.strftime('%Y-%m-%d')
    for front_month in range(1,6):
        quandl_code = 'CHRIS/CME_UB{num}'.format(num=str(front_month))
        try:
            data = quandl.get(quandl_code, authtoken=config.get('quandl', 'token'), start_date=start_date)
            month_array.append(front_month)
            last_settle.append(data['Settle'].iloc[-1])
        except Exception as e:
            print(quandl_code + str(e))
    forward_curve = []
    for month, settle in zip(month_array, last_settle):
        # print(str(month) + ' -> ' + str(settle))
        forward_curve.append((month, settle))
    return forward_curve
