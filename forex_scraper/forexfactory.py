"""
Forexfactory adapter

"""

from bs4 import BeautifulSoup
import requests
import datetime
import logging
import csv
import dataset
import sys
import configparser

class ForexFactory:

    def __init__(self):
        # construct start link and end link for calendar scraping
        start_of_week = datetime.datetime.now() + datetime.timedelta(days=(datetime.datetime.now().weekday() - 6))
        mon = start_of_week.strftime('%b').lower()
        day = start_of_week.strftime('%d').lstrip('0')
        year = start_of_week.strftime('%Y')
        self.startlink = 'calendar.php?week=' + mon + day + '.' + year

    def get_economic_calendar(self):
        logger = logging.getLogger()
        # write to console current status
        logger.info("Scraping data for link: {}".format(self.startlink))

        # get the page and make the soup
        base_url = "https://www.forexfactory.com/"
        r = requests.get(base_url + self.startlink)
        data = r.text
        soup = BeautifulSoup(data, "lxml")

        # get and parse table data, ignoring details and graph
        table = soup.find("table", class_="calendar__table")

        # do not use the ".calendar__row--grey" css selector (reserved for historical data)
        trs = table.select("tr.calendar__row.calendar_row")
        fields = ["date", "time", "currency", "impact", "event", "actual", "forecast", "previous"]

        # some rows do not have a date (cells merged)
        curr_year = self.startlink[-4:]
        curr_date = ""
        curr_time = ""
        news_data = []
        for tr in trs:

            # fields may mess up sometimes, see Tue Sep 25 2:45AM French Consumer Spending
            # in that case we append to errors.csv the date time where the error is
            try:
                for field in fields:
                    data = tr.select("td.calendar__cell.calendar__{}.{}".format(field, field))[0]
                    # print(data)
                    if field == "date" and data.text.strip() != "":
                        curr_date = data.text.strip()
                    elif field == "time" and data.text.strip() != "":
                        # time is sometimes "All Day" or "Day X" (eg. WEF Annual Meetings)
                        if data.text.strip().find("Day") != -1:
                            curr_time = "12:00am"
                        else:
                            curr_time = data.text.strip()
                    elif field == "currency":
                        currency = data.text.strip()
                    elif field == "impact":
                        # when impact says "Non-Economic" on mouseover, the relevant
                        # class name is "Holiday", thus we do not use the classname
                        impact = data.find("span")["title"]
                    elif field == "event":
                        event = data.text.strip()
                    elif field == "actual":
                        actual = data.text.strip()
                    elif field == "forecast":
                        forecast = data.text.strip()
                    elif field == "previous":
                        previous = data.text.strip()
                dt = datetime.datetime.strptime(",".join([curr_year, curr_date, curr_time]), "%Y,%a%b %d,%I:%M%p")
                news_object = {'date': dt.strftime('%Y-%m-%d'), 'time': curr_time, 'currency': currency, 'impact': impact,
                               'event': event, 'actual': actual, 'forecast': forecast, 'previous': previous}
                news_data.append(news_object)
                logging.info(news_object)
            except:
                with open("errors.csv", "a") as f:
                    csv.writer(f).writerow([curr_year, curr_date, curr_time])

        logger.info("Successfully retrieved data")
        return news_data