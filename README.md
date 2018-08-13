# DD1349

This project aims to build a tool that with the help of machine learning helps the user to make good day trades on the stock market. This is done by looking at historical data and from that predict the next days highest and lowest share prices. This information will be used to tell the user to buy when the price is far from the highest predicted price, and sell when it is close to the same price.

## Installation

First off we need to make sure that ```sci-kit learn``` is installed.

```
pip install scikit-learn
```

When that is done, all you have to do is to download the project source code and you are done.

## Using the program

To use the program the user have to decide which market the program should work on. This is done with the```-m``` flag, the following markets are available *Stockholm*, *Copenhagen*, *Helsinki* and *Iceland*. To start you would use the following command (With of course your market of choice):

```
python3 main.py -m Stockholm
```
### Sample output
```
2017-05-18 11:09:00
+--------------------------------------------------------------------+
|                             *** BUY ***                            |
+--------------+---------------+----------------+--------------------+
| Stock symbol | Current price | Predicted high | Potentiall earning |
+--------------+---------------+----------------+--------------------+
|      AHSL.ST |     57.35 SEK |      59.76 SEK |             4.20 % |
|  ALIV-SDB.ST |    904.00 SEK |     931.95 SEK |             3.09 % |
|    ATCO-A.ST |    314.90 SEK |     323.42 SEK |             2.71 % |
+--------------+---------------+----------------+--------------------+
```