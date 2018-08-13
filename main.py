from harvest_data import *
from predictions import *
import argparse
import os

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-m", nargs=1, choices=["Stockholm", "Copenhagen", "Helsinki", "Iceland"], type=str, metavar="Market", help="Available markets are [Stockholm, Copenhagen, Helsinki, Iceland]", required=True)
args = parser.parse_args()


def get_historical_data(stock_symbols):
    # Collects historical quotes for each company and converts it to percentage change since last days closing price.
    historical_quotes = {}
    date_indexes = {}
    percentage_quotes = {}
    i = 0
    for stock_symbol in stock_symbols:
        historical_quotes[stock_symbol],date_indexes[stock_symbol] = get_historical_quotes(stock_symbol)
        percentage_quotes[stock_symbol] = quotes_to_percentage_change(historical_quotes[stock_symbol])
        i+=1
        print("Collecting data:%20s %7.2f %%                                \r" % (stock_symbol, 100*(i / len(stock_symbols))), end="")
    print()
    return historical_quotes, date_indexes, percentage_quotes

def wait_function(time_interval):
    # Makes the program wait for time_interval seconds (0-59) seconds.
    s = int(datetime.now().second/time_interval)
    while int(datetime.now().second/time_interval) == s:
        pass

def print_buys(buy,predictions,latest_quotes):
    # Prints good potentiall Buys
    print("""%s
+--------------------------------------------------------------------+
|                             *** BUY ***                            |
+--------------+---------------+----------------+--------------------+
| Stock symbol | Current price | Predicted high | Potentiall earning |
+--------------+---------------+----------------+--------------------+""" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    for b in buy:
        predH = (1 + predictions[b][1]) * latest_quotes[b]['previousClose']
        potEarn = (predH - latest_quotes[b]['lastTrade'])/latest_quotes[b]['lastTrade']
        print("| %12s | %9.2f SEK | %10.2f SEK | %16.2f %% |" % (b, latest_quotes[b]['lastTrade'], predH, 100*potEarn))
    print("+--------------+---------------+----------------+--------------------+")
    
    
def main():
    os.system('clear')

    # Learning parameters
    n_prev_days = 1
    k = 7
    
    # 
    market = args.m[0]
    predictions = {}
  
    hours = get_opening_hours(market)
    hours = [datetime(2017, 5, 18, 0, 0), datetime(2017, 5, 18, 17, 0)]
    stock_symbols = get_listed_stocks(market)[:10]
    last_trade_day = datetime(2000,1,1).date()# TODO, since some data seems not to be up to date, this is necessary to make valid predictions (The predictions will probably not be as good as they can if a couple of trade days have passed since last data update).

    historical_quotes,date_indexes, percentage_quotes = get_historical_data(stock_symbols)
    
    X,Y,x = make_training_data(stock_symbols, percentage_quotes, n_prev_days) # X = Training data, Y = Target data, x = 
    predictions = predict(k,X,Y,x,stock_symbols)

    #Wait until market opens
    
    while market_open(hours):
        
        latest_quotes = get_latest_quotes(stock_symbols)
        buy = find_buys(predictions, latest_quotes, stock_symbols)
        os.system('clear')
        print_buys(buy,predictions,latest_quotes)
        wait_function(15)

    #TODO Wait til next day.

        
main()
