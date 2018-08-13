from harvest_data import *
from predictions import *
from sklearn.neighbors import KNeighborsRegressor as classifier
#from sklearn.ensemble import ExtraTreesRegressor as classifier
import argparse
from datetime import timedelta
from math import sqrt


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-m", nargs=1, choices=["Stockholm", "Copenhagen", "Helsinki", "Iceland"], type=str, metavar="Market", help="Available markets are [Stockholm, Copenhagen, Helsinki, Iceland]", required=True)
args = parser.parse_args()

def mtd(stock_symbols, percentage_quotes, n_prev_days, d, date_indexes):
    # mtd short for make_training_data (function in predictions.py) this is a version more suitable for testing (possible to set start and end dates).
    X = []
    Y = []
    x = {}
    y = {}

    for stock_symbol in stock_symbols:
        # prepares data for training and predictions
        
        if d in date_indexes[stock_symbol]:
            ind = date_indexes[stock_symbol][d]
            
            Y += percentage_quotes[stock_symbol][ind+1:-n_prev_days]
            X += [sum(percentage_quotes[stock_symbol][i:n_prev_days+i],[]) for i in range(2+ind,len(percentage_quotes[stock_symbol])-n_prev_days+1)]
            x[stock_symbol] = sum(percentage_quotes[stock_symbol][ind+1:ind+1+n_prev_days], [])
            y[stock_symbol] = percentage_quotes[stock_symbol][ind]

    return X,Y,x,y

def test_loop(d,ld,RMSE,AD,cnt,stock_symbols, percentage_quotes, n_prev_days, date_indexes, k):
    # Makes predictions, and compare with actual outcome. Also some error calculations.
    while d < ld:
        predictions = {}
        d += timedelta(days=1)

        X,Y,x,y = mtd(stock_symbols, percentage_quotes, n_prev_days, d, date_indexes)
        predictions = predict(k,X,Y,x,stock_symbols)
        
        for stock_symbol in stock_symbols:
            if stock_symbol in predictions:
                p = predictions[stock_symbol]
                r = y[stock_symbol]
                RMSE += sum([(p[i]-r[i])**2 for i in range(0,4)])
                AD += sum([abs(p[i]-r[i]) for i in range(0,4)])
                cnt += 4
    return RMSE, AD, cnt


def test():
    # Test to find the best parameters (k and n_prev_days)
    market = args.m[0]
    historical_quotes = {}
    date_indexes = {}
    percentage_quotes = {}

    stock_symbols = get_listed_stocks(market)

    for stock_symbol in stock_symbols:
        historical_quotes[stock_symbol], date_indexes[stock_symbol] = get_historical_quotes(stock_symbol)
        percentage_quotes[stock_symbol] = quotes_to_percentage_change(historical_quotes[stock_symbol])

    n_prev_days = 3
    k = 9
    for k in range(1,9):
        RMSE = 0
        AD = 0
        cnt = 0
        d = datetime(2016,1,1).date()
        ld = datetime(2016,12,31).date()
        RMSE, AD, cnt = test_loop(d,ld,RMSE,AD,cnt,stock_symbols, percentage_quotes, n_prev_days, date_indexes, k)

        RMSE = sqrt(RMSE/cnt)
        AD = AD / cnt
    
        print("RMSE: %8.4f | AD: %8.4f | k: %5d | n: %5d | count: %10d" % (float(100*RMSE), float(AD), k, n_prev_days, (cnt/4)))
test()
