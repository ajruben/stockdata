import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import pytz
from scipy import stats
from pandas_datareader import data as pdr
import functools 
yf.pdr_override()
import matplotlib.pyplot as plt
import os 

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
        self.figures_directory = 'figures'

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
    def linear_regression(self, company_name, index_name, plot=False): #usually company index, but can alos be company company, index index, index company.
        """
        background: https://www.probabilitycourse.com/chapter8/8_5_2_first_method_for_finding_beta.php
        """
        
        if self.log is None:
            raise ValueError('self.log is None. First run self.get_data() and get_return().')
        
        lin_dict = {}
        for key, return_data in zip(["log return", "normal return", "double derivative return"],[self.log, self.nreturn, self.n2return]):
            #prep data
            company = return_data.loc[:, company_name].values
            index = return_data.loc[:, index_name].values
            #all calculations
            cov = np.cov(index, company)
            beta1 = cov[1,0]/cov[0,0]
            beta0 =  company.mean() - beta1*index.mean()
            r_sq = (cov[1,0])**2 /(cov[0,0]*cov[1,1])
            vol_daily = index.std()
            vol_period = vol_daily*np.sqrt(len(index))
            #store results
            linear_regression = {'covmat':cov, 'beta1' : beta1, 'beta0' : beta0, 'r_sq' : r_sq, 'vol_daily' : vol_daily, 'vol_period': vol_period, 
                                 'company':company_name, 'index':index_name, 'company_returns':company, 'index_returns':index}
            lin_dict[key] = linear_regression
        self.linear_regression = lin_dict
        
        if plot:
            #check output directory figures.
            if not os.path.exists(self.figures_directory):
                os.makedirs(self.figures_directory)
            for key in self.linear_regression:
                self._plot_regression(self.linear_regression[key], type_return = key)

    def _plot_regression(self, lineair_regression_result, type_return):
        #data
        ret_index = lineair_regression_result['index_returns']
        ret_company = lineair_regression_result['company_returns']
        
        #init figure, create scatter
        plt.figure()
        plt.scatter(ret_index, ret_company, label='return on a given day', color='blue', marker='.')

        #borders and regression line
        x_min = (ret_index.min()) - (ret_index.max()*0.2)
        x_max = (ret_index.max()) * 1.2
        y_min = (ret_company.min()) - (ret_company.max()*0.2)
        y_max = (ret_company.max()) * 1.2
        x_line = np.linspace(x_min-1, x_max+1, num=2)
        y_line = lineair_regression_result['beta0'] + (lineair_regression_result['beta1'] * x_line)  
        plt.plot(x_line, y_line, label='Linear regression', color='red')
        
        # layout
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xlabel(f'{lineair_regression_result['index']}-axis')
        plt.ylabel(f'{lineair_regression_result['company']}-axis')
        plt.title(f'Linear regression for {type_return}: {lineair_regression_result['company']} and {lineair_regression_result['index']} between {str(self.start)[:10]} and {str(self.end)[:10]}')
        plt.legend()

        # Save and close
        plt.savefig(f'{self.figures_directory}/linear_regression_{type_return}_{lineair_regression_result['company']}_{lineair_regression_result['index']}_{str(self.start)[:10]}_{str(self.end)[:10]}.png')
        plt.close()

if __name__ == '__main__':
    stock = Stock(add=[])
    stock.get_data()
    stock.get_return()
    stock.linear_regression('AAPL', '^GSPC', plot=True)
    #print(stock.overview)
