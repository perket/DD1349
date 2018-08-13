import numpy as np
from sklearn.neighbors import KNeighborsRegressor as KNR
#from sklearn.tree import ExtraTreeRegressor as ETR
from sklearn.neural_network import MLPRegressor as MLPR
from decimal import Decimal as D


def make_training_data(stock_symbols, percentage_quotes, n_prev_days):
    # Processes the data in order to make predictions.
    X = []
    Y = []
    x = {}
    
    i = 0
    for stock_symbol in stock_symbols:
        # prepares data for training and predictions
        i += 1
        print("Preparing data: %20s %7.2f %%                  \r" % (stock_symbol, 100*i/len(stock_symbols)),end="")
        Y += percentage_quotes[stock_symbol][:-n_prev_days]
        X += [sum(percentage_quotes[stock_symbol][i:n_prev_days+i],[]) for i in range(1,len(percentage_quotes[stock_symbol])-n_prev_days+1)]
        x[stock_symbol] = sum(percentage_quotes[stock_symbol][0:n_prev_days], [])
        
    print()
    return X,Y,x


def quote_to_percentage(q):
    # Calculate the daily percentage change on a stock compared to yesterdays closing price.
    percentage_quotes = {}
    percentage_quotes['high'] = q['high']/q['previousClose'] - 1
    percentage_quotes['low'] = q['low']/q['previousClose'] - 1
    percentage_quotes['lastTrade'] = q['lastTrade']/q['previousClose'] - 1
    return percentage_quotes

def find_buys(predictions,latest_quotes,stock_symbols):
    # Uses some rules to determine if a stock is worth buying or not.
    buy_sell_margin = D(.015)
    buy = []
    
    for stock_symbol in stock_symbols:
        p = predictions[stock_symbol]
        q = latest_quotes[stock_symbol]
        high_low_margin = (p[1]-p[2]) * D(.15)
        q = quote_to_percentage(q)
        
        if p[1] - p[2] > buy_sell_margin + 2 * high_low_margin and q['high'] < p[1] - high_low_margin and q['low'] > p[2] - high_low_margin:
            if q['lastTrade'] < p[1] - buy_sell_margin and q['high'] < p[1] - high_low_margin:
                buy.append(stock_symbol)
            
    return buy

def predict(k,X,Y,x,stock_symbols):
    #Makes predictions, creates a classifier, fits the training and target data, and then predicts next days EODs.
    predictions = {}
    clf = KNR(n_neighbors=k) # maybe activate weights='distance'
    #clf = MLPR(hidden_layer_sizes=(8,4),max_iter=10000)
    
    if len(X) > 0 and len(X) == len(Y):
        clf.fit(X,Y)
        X_width = len(X[0])
        i = 0
        for stock_symbol in stock_symbols:
            i += 1
            if stock_symbol in x:
                print("Predicting:     %20s %7.2f %%                  \r" % (stock_symbol, 100*i/len(stock_symbols)),end="")
                if len(x[stock_symbol]) == X_width:
                    predictions[stock_symbol] = clf.predict([x[stock_symbol]])[0]
        print()
    return predictions
