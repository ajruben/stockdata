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
import matplotlib.dates as mdates
import os 

class Portfolio():
    def __init__(self, tickers):
        self.start = dt.datetime(2022,1,1)
        self.end = dt.datetime.now()
        self.big_tickers = ['^GSPC','TSLA', 'AAPL','AMZN','GOOGL']#'F','GM','LYFT','JPM','GS','KO'] #for now work with this.
        if tickers is None:
            self.tickers = self.big_tickers
        else:
            self.tickers = tickers
        self.data = None
        self.log = None
        self.nreturn = None
        self.n2return = None
        self.overview = None
        self.figures_directory = 'figures'
        self.relative_return = None
        self.linear_regression_data = None

    #@functools.cached_property
    def get_data(self):
        self.data = pdr.get_data_yahoo(self.tickers, self.start, self.end, pd.to_timedelta)
        self.relative_return = self.data['Close']/self.data['Close'].iloc[0]
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
            linear_regression_ = {'covmat':cov, 'beta1' : beta1, 'beta0' : beta0, 'r_sq' : r_sq, 'vol_daily' : vol_daily, 'vol_period': vol_period, 
                                 'company':company_name, 'index':index_name, 'company_returns':company, 'index_returns':index}
            lin_dict[key] = linear_regression_
        self.linear_regression_data = lin_dict
        
        if plot:
            #check output directory figures.
            if not os.path.exists(self.figures_directory):
                os.makedirs(self.figures_directory)
            for key in self.linear_regression_data:
                self._plot_regression(self.linear_regression_data[key], type_return = key)

        return lin_dict

    def plot_relative(self, tickers = None, file_name = None):
        """
        Plots relative return since a starting date. can pass your own filename to save to plot to (end with .png or .jpg)
        """
        if self.relative_return is not None:
            if tickers is None:
                tickers = self.tickers
            plt.figure()
            for ticker in tickers:
                x = self.relative_return.index
                y = self.relative_return[ticker]
                plt.plot(x,y, label=f"{ticker}")
            
            plt.title('return in percentage compared to starting date.')
            plt.grid()
            plt.legend()
            
            # Set ticks and labels
            ax = plt.gca()
            ax.xaxis.set_major_locator(mdates.YearLocator(1))  # Set major ticks at each year
            ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=-1))  # Set minor ticks at each month end
            ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.YearLocator()))

            # Rotate x-axis labels for better readability (optional)
            plt.xticks(rotation=45, ha='right')

            # Save and close
            if file_name is None:
                file_name = f'{self.figures_directory}/relative_return_{str(self.start)[:10]}_{str(self.end)[:10]}.png'

            plt.savefig(file_name, dpi=300, bbox_inches='tight', pad_inches=0.1)
            plt.close()
        else:
            raise ValueError('self.data is None. First run self.get_data().')
    
    def stock_portfolio(self, units, index_ticker, direction, type_return = 'log return', randomize = False):
        #data check
        if self.data is None:
            self.data = self.get_data()
        
        
        #randomize or not?
        if randomize:
            pass
        
        else:
            #convert to npy array
            beta_list = []
            names = []
            for ticker in self.tickers:
                if ticker == index_ticker: #index_ticker not part of portfolio, just needed for linear regression
                    continue
                lin_dict = self.linear_regression(index_name = index_ticker, company_name = ticker, plot=False) #check lin_regres
                #for now take log
                beta1 = lin_dict[type_return]['beta1']
                beta_list.append(beta1)
                names.append(ticker)
                    
            if type(units) == type([]):
                units = np.array(units)
        
            final_prices = self.data['Close'].loc[self.data['Close'].index[-1], names].tolist()
            value = units*final_prices #vectorized
            weights = [round(val/sum(value),2) for val in value]
            
        
        self.stockport = pd.DataFrame({
            'Stock': names,
            'Direction': direction,
            'Stock price': final_prices,
            'Units': units,
            'Value': value,
            'Weights' : weights,
            'Beta': beta_list
           # 'Weighted beta': weights*beta1
        })


        
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
        plt.grid()
        plt.legend()

        # Save and close
        plt.savefig(f'{self.figures_directory}/linear_regression_{type_return}_{lineair_regression_result['company']}_{lineair_regression_result['index']}_{str(self.start)[:10]}_{str(self.end)[:10]}.png',
                    dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()
    
    

if __name__ == '__main__':
    stock = Portfolio(tickers = None)
    stock.get_data()
    stock.get_return()
    stock.plot_relative()
    stock.stock_portfolio(units = [100]*(len(stock.tickers)-1), direction = 'Long', index_ticker='^GSPC')
    print(stock.stockport)
    #print(stock.overview)
