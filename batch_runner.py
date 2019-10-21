"""
Runner for batch mode

"""

from utils import prepare_logger
from forex_scraper import forexfactory
from quandl_futures import get_quandl_futures as gq

QUANDL_CONFIG = '../quandl.conf'


if __name__ == '__main__':
    logger = prepare_logger.get_logger()
    ff_scraper = forexfactory.ForexFactory()
    news_date = ff_scraper.get_economic_calendar()
    brent_curve = gq.get_brent_cme_forward(QUANDL_CONFIG)
    print(brent_curve)
