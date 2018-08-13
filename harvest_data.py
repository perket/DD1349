from datetime import *
from time import *
import requests as req
import urllib.request
import urllib.error
from lxml import etree
from lxml import html
from io import StringIO, BytesIO
import logging
from decimal import Decimal as D
from dateutil.parser import parse
import re

# Just to get rid of some debbuging information
logging.getLogger("requests").setLevel(logging.WARNING)

# Initializes a url opener
request_headers = {
'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.74.9 (KHTML, like Gecko) Version/7.0.2 Safari/537.74.9', 
'Referer': 'http://python.org'
}
url_opener = urllib.request.build_opener()


def get_todays_date():
    # returns current date
    d = datetime.now()
    dd = d.date()
    return dd


def get_market_source_url(market):
    # sources contains urls to sources of listed companies on different markets
    sources = {
"Stockholm" : "http://www.nasdaqomxnordic.com/shares/listed-companies/stockholm",
"Copenhagen" : "http://www.nasdaqomxnordic.com/aktier/listed-companies/copenhagen",
"Helsinki" : "http://www.nasdaqomxnordic.com/aktier/listed-companies/helsinki",
"Iceland" : "http://www.nasdaqomxnordic.com/aktier/listed-companies/iceland",
}
    return sources[market]


def get_stock_symbol_ending(market):
    # Returns YQL stock symbol market ending (To find a companie listed on the Stockholm market we need to add .ST to the end of the symbol e.g. ABB becomes ABB.ST)
    symbol_endings = {
"Stockholm" : "ST",
"Copenhagen" : "CO",
"Helsinki" : "HE",
"Iceland" : "IC"
}
    return symbol_endings[market]


def get_market_schedule_table_order(market):
    # In order to get the correct opening hours we need to know which column to look in, this returns the column number coresponding to each market.
    table_order = {
"Stockholm" : 1,
"Copenhagen" : 2,
"Helsinki" : 3,
"Iceland" : 4
}
    return table_order[market]


def get_listed_stocks(market):
    # Should collect all listed companies on a given market and return a list with each companys stock symbol (e.g. AAPL for the apple stock).
    stock_symbols = []
    source = get_market_source_url(market)

    html = open_url(source)
    trs = html.xpath('.//table[contains(@id,"listedCompanies")]//tr')[1:]
    symbol_ending = get_stock_symbol_ending(market)

    for tr in trs:
        stock_symbols.append("%s.%s" % (tr.xpath('.//td[2]//text()')[0].replace(" ","-"), symbol_ending))

    return stock_symbols


def get_holidays(market, html, year):
    # Returns a dictionary containing dates as index and if the market is closed (0) or a half day (.5) as value for corespondig date.
    holidays = {}

    # Well this is a messy row, and Im lazy. But this lines extract the cell from a table that contains all holiday opening hours info of our market of choice. 
    td = html.xpath('.//h3[contains(text(), "Exchange holiday schedule %d")]/../..//h4[contains(text(), "%s")]/../..//td' % (year,market))[1] 
    paragraphs = td.xpath('.//p/text()')
    paragraphs = [x.strip().split(", ") for x in paragraphs]
    
    for d in paragraphs[0]:
        # Not 100 % confident that this parse thing is the best tool for this, but it seems to work for now.
        holidays[parse("%d %s" % (year, d)).date()] = 0
    
    if len(paragraphs) == 2:
        for d in paragraphs[1]:
            holidays[parse("%d %s" % (year, d)).date()] = .5

    return holidays


def set_opening_hours(opens, closes, hours_text):
    # Adds opening/closing hours and minutes to opening/closing datetime objects from string.
    oh, om = [int(x) for x in hours_text[0].replace(".",":").split(":")]
    ch, cm = [int(x) for x in hours_text[1].replace(".",":").split(":")]
    opens = opens.replace(hour=oh, minute=om)
    closes = closes.replace(hour=ch, minute=cm)

    return opens, closes


def get_opening_hours(market):
    # Should return the opening hours for a market on the current day as a tuple (hh:mm:ss, hh:mm:ss)
    table_column = get_market_schedule_table_order(market)

    source = "http://www.nasdaqomxnordic.com/oppettider"
    today = get_todays_date()
    opens = closes = datetime(today.year, today.month, today.day, 0, 0, 0)
    
    html = open_url(source)
    holidays = get_holidays(market, html, today.year)
    
    if not today in holidays:
        regular_hours_text = html.xpath('(.//td[text()="Equities"])[1]/..//td[%d]/text()' % (table_column + 1))[0]
        opens, closes = set_opening_hours(opens, closes, regular_hours_text.strip().split("-"))
        
    elif holidays[today] == .5:
        regular_hours_text = html.xpath('(.//b[text()="Half day trading hours"])/../../..//tr[2]//p[1]/text()')[0]
        opens, closes = set_opening_hours(opens, closes, regular_hours_text.strip().split("-"))

    return [opens, closes]


def market_open(hours):
    # Checks if market is open right now 
    now = datetime.now()
    return hours[0] <= now and now <= hours[1]


def open_url(url):
    # Opens url and return content 
    request = urllib.request.Request(url, headers=request_headers)
    error = False
    downloaded_data = False
    found = False
    i = 0
    while found == False and i < 10:
        try:
            downloaded_data = url_opener.open(request)           
            downloaded_data = parseHTML(downloaded_data)
            found = True
        except Exception as e:
            error = e
            i += 1
    if found == False:
        print(error)
    return downloaded_data


def parseHTML(data):
    # Parse html string to searchable xml-tree
    html = str(data.read(),encoding='utf8')
    parser = etree.HTMLParser()
    try:
        return etree.parse(StringIO(html),parser) 
    except:
        return html

def get_latest_quotes(stock_symbols):
    # Returns latest stock quotes
    url = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=sl1pgh" % "+".join(stock_symbols)

    csv = req.get(url)
    data = csv.text.strip().replace('"','').split('\n')
    latest_quotes = [row.split(',') for row in data]
    
    # Column 0 = stock symbol, 41 = Latest trade price , ? = Previous close
    return {quote[0] : {'lastTrade' : D(quote[1]), 'previousClose' : D(quote[2]), 'low' : D(quote[3]), 'high' : D(quote[4])} for quote in latest_quotes}


def get_historical_quotes(stock_symbol):
    # Gets all EOD (end of day) data for company associated with stock_symbol
    url = "http://212.107.142.115/stock_backup/%s.csv" % stock_symbol # This is a backup url, only holding the 10 first stocks on the Stockholm exchange. Last updated 2017-05-17.
    #url = "http://ichart.finance.yahoo.com/table.csv?s=%s" % stock_symbol
    
    csv = req.get(url)
    if csv.status_code == 200:
        data = csv.text
        regex = '(?m)^.*(null)+.*\n' # Part of backup fix
        data = re.sub(r'%s' % regex, '' ,data) # Part of backup fix
        data = data.strip().split('\n')[1:][::-1] # The [::-1] is also part of backup fix
        # Open, High, Low, Close
        
        dates = {parse(x.split(',')[0]).date() : (data.index(x)-1) for x in data}
        quotes = [[D(x) for x in row.split(',')[1:5]] for row in data]

        return quotes,dates
    return [],{}


def quotes_to_percentage_change(quotes):
    # Calculates the percentage difference to previous days closing price
    q_num = len(quotes)
    i = 0
    percentage_quotes = []
    while i < q_num - 1:
        last_close = quotes[i+1][3]
        percentage_quotes.append([(q/last_close)-1 for q in quotes[i]])
        i += 1
    percentage_quotes.append([D(0), D(0), D(0), D(0)])
    return percentage_quotes
