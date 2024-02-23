import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import pytz
from scipy import stats
from pandas_datareader import data as pdr
import functools 
yf.pdr_override()

class Stock():
    def __init__(self, add):
        self.start = dt.datetime(2022,1,1)
        self.end = dt.datetime.now()
        self.big = ['^GSPC','TSLA', 'AAPL','AMZN','GOOGL','F','GM','LYFT','JPM','GS','KO'] #for now work with this.
        self.add = add
        self.data = None
        self.log = None
        self.nreturn = None
        self.n2return = None
        self.overview = None

    #@functools.cached_property
    def get_data(self):
        self.data = pdr.get_data_yahoo(self.big, self.start, self.end, pd.to_timedelta)
        return self.data
    
    #@functools.cached_property
    def get_return(self):
        if self.data is not None:
            self.log = (np.log(self.data['Close']/self.data['Close'].shift(1))).dropna()
            self.nreturn = ((self.data.Close - self.data.Close.shift(1))/self.data.Close.shift(1)).dropna()
            self.n2return = (self.nreturn - self.nreturn.shift(1)/self.nreturn.shift(1)).dropna()  #double derivative
        else:
            raise ValueError('self.data is None. First run self.get_data().')

    #@functools.cached_property
    def calculate_betas(self, company, index): #usually company index, but can alos be company company, index index, index company.
        #select data into np array to prep for calculations
        if self.log is None:
            raise ValueError('self.log is None. First run self.get_data() and get_return().')
        
        npa_log_company = self.log.loc[:,company].values
        npa_log_index = self.log.loc[:,index].values
        #execute
        cov = np.cov(npa_log_index, npa_log_company)
        beta1 = cov[1,0]/cov[0,0]
        beta0 =  npa_log_company.mean() - beta1*npa_log_index.mean()
        r_sq = (cov[1,0])**2 /(cov[0,0]*cov[1,1])
        vol_daily = npa_log_index.std()
        vol_period = vol_daily*np.sqrt(len(npa_log_index))
        #store
        self.overview = {'beta1' : beta1, 'beta0' : beta0, 'r_sq' : r_sq, 'vol_daily' : vol_daily, 'vol_period': vol_period}
        



if __name__ == '__main__':
    stock = Stock(add=[])
    stock.get_data()
    stock.get_return()
    stock.calculate_betas('AAPL', '^GSPC')
    print(stock.overview)
