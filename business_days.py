import numpy as np
import pandas as pd
import math
from datetime import *
from dateutil.relativedelta import * #https://dateutil.readthedocs.io/en/stable/relativedelta.html

class CountryHoliday:
    def __init__(self):
        pass

    def _IsHoliday_(self,date,calendar):
        # check if date is a weekend
        weekdays = [0,1,2,3,4]
        if not date.weekday() in weekdays:
            return False
        
        # check if date is a holiday
        y = date.year
        m = date.month
        d = date.day
        wkd = date.weekday()

        if calendar == 'NY':
            if (m==1 and d==1) or (m==12 and d==31 and wkd==4) or \
                (m==1 and d==2 and wkd==0):
                return True
            # Martin Luther King, third Monday of January
            if m==1 and wkd==0 and (d>14 and d<22):
                return True
            # Washington's Birthday, third Monday of February
            if m==2 and wkd==0 and (d>14 and d<22):
                return True
            # Memorial Day, last Monday of May
            if m==5 and wkd==0 and d>24:
                return True
            # Independence Day, July 4
            if (m==7 and d==4) or (m==7 and d==3 and wkd==4) or \
                (m==7 and d==5 and wkd==0):
                return True
            # Labor Day, the first Monday of September
            if m==9 and wkd==0 and d<8:
                return True
            # Columbus Day, second Monday of October
            if m==10 and wkd==0 and (d>7 and d<15):
                return True
            # Veterans Day, November 11
            if (m==11 and d==11) or (m==11 and d==10 and wkd==4) or \
                (m==11 and d==12 and wkd==0):
                return True
            # Thanksgiving Day, fourth Thursday of November
            if m==11 and wkd==3 and (d>21 and d<29):
                return True
            # Christmas Day, December 25
            if (m==12 and d==25) or (m==12 and d==24 and wkd==4) or \
                (m==12 and d==26 and wkd==0):
                return True
    
        return False
    

class CurveDate(CountryHoliday):
    def __init__(self):
        pass

    def _IsWeekend_(self,date):
        weekdays = [0,1,2,3,4]
        return date.weekday() not in weekdays
    
    def _AddBusinessDays_(self,date,numdays,busdaysconv,calendar):
        next_day = date
        for i in range(numdays):
            next_date = next_date + relativedelta(days=+1)
            while (self._IsWeekend_(next_date)) or (self._IsHoliday_(next_date,calendar)):
                next_date = next_date + relativedelta(days=+1)
        return next_date
    
    def _AddBusinessMonths_(self,date,nummonths,busdaysconv,calendar):
        next_date = date
#         for i in range(numyears):
        next_date = next_date + relativedelta(months=+nummonths)
        while (self._IsWeekend_(next_date)) or (self._IsHoliday_(next_date,calendar)):
            next_date = next_date + relativedelta(days=+1)
        return next_date
    
    def _AddBusinessYears_(self,date,numyears,busdayconv,calendar):
        next_date = date
#         for i in range(numyears):
        next_date = next_date + relativedelta(years=+numyears)
        while (self._IsWeekend_(next_date)) or (self._IsHoliday_(next_date,calendar)):
            next_date = next_date + relativedelta(days=+1)
        return next_date
    
    def _YFrac_(self, date1,date2,daycountconvention):
        if daycountconvention == 'ACTACT':
            pass
        elif daycountconvention == 'ACT365':
            # the difference between two datetime objects is a timedelta object
            delta = date2-date1
            delta_fraction = delta.days / 365.0
            return delta_fraction
        elif daycountconvention == 'ACT360':
            # the difference between two datetime objects is a timedelta object
            delta = date2-date1
            delta_fraction = delta.days / 360.0
            return delta_fraction 
        elif daycountconvention == 'Thirty360':
            pass
        else:
            # the difference between two datetime objects is a timedelta object
            delta = date2-date1
            delta_fraction = delta.days / 360.0
            
            return delta_fraction


class YieldCurve(CurveDate,CountryHoliday):
    def __init__(self):
        self.dfcurve = pd.DataFrame() # initialize dataframe for curve data
    
    def __GetSwapCurveData__(self):
        filein = 'swapcurvedata.xlsx'
        self.dfcurve = pd.read_excel(filein, sheet_name='curvedata', index_col='Tenor')
        self.dfcurveparams = pd.read_excel(filein, sheet_name='curveparams')
        self.dfcurveparams.loc[self.dfcurveparams.index[0], 'Date'] = date.today()
        
        busdayconv = self.dfcurveparams['BusDayConv'].iloc[0]
        calendar = self.dfcurveparams['Calendar'].iloc[0]
        curvedate = self.dfcurveparams['Date'].iloc[0]
        while (self._IsWeekend_(curvedate) or self._IsHoliday_(curvedate,calendar)):
            curvedate = curvedate + relativedelta(days=+1)
        curvesettledays = self.dfcurveparams['SettleDays'].iloc[0]
        curvesettledate = self._AddBusinessDays_(curvedate,curvesettledays,busdayconv,calendar)
        
    self.dfcurveparams.loc[self.dfcurveparams.index[0], 'SettleDate'] = \   curvesettledate



    def _DatesForTenors_(self):
            curvesettledate = self.dfcurveparams['SettleDate'].iloc[0]
            busdayconv = self.dfcurveparams['BusDayConv'].iloc[0]
            calendar = self.dfcurveparams['Calendar'].iloc[0]
            
            self.dfcurve.loc[self.dfcurve.index=='ON', 'Date'] = \
                            self._AddBusinessDays_(curvesettledate,1,busdayconv,calendar)
            self.dfcurve.loc[self.dfcurve.index=='1W', 'Date'] = \
                            self._AddBusinessDays_(curvesettledate,5,busdayconv,calendar)
            for i in range (len(self.dfcurve)):
                if self.dfcurve.index[i][-1] == 'M':
                    num = int(self.dfcurve.index[i][:-1])       
                    self.dfcurve.loc[self.dfcurve.index[i],'Date'] = \
                            self._AddBusinessMonths_(curvesettledate,num,busdayconv,calendar)
                elif self.dfcurve.index[i][-1] == 'Y':
                    num = int(self.dfcurve.index[i][:-1])       
                    self.dfcurve.loc[self.dfcurve.index[i],'Date'] = \
                    self._AddBusinessYears_(curvesettledate,num,busdayconv,calendar)


    def _YearFractions_(self):
            curvesettledate = self.dfcurveparams['SettleDate'].iloc[0]
            for i in range(len(self.dfcurve)):
                daycntconv = self.dfcurve['Daycount'].iloc[i]
                if i == 0:
                    self.dfcurve.loc[self.dfcurve.index[i],'YearFraction'] = \
                        self._YFrac_(curvesettledate, self.dfcurve['Date'].iloc[i], daycntconv)  
                else:
                    self.dfcurve.loc[self.dfcurve.index[i], 'YearFraction'] = \
                        self._YFrac_(self.dfcurve['Date'].iloc[i-1], self.dfcurve['Date'].iloc[i], daycntconv)
                self.dfcurve.loc[self.dfcurve.index[i], 'CumYearFraction'] = \
                self._YFrac_(curvesettledate, self.dfcurve['Date'].iloc[i], 
                            daycntconv)
    fileout = "yieldcurve.xlsx"
    self.dfcurve.to_excel(fileout, sheet_name='yieldcurve', index=True)


    def _ZeroRates_(self):
        for i in range(len(self.dfcurve)):
            if self.dfcurve['Type'].iloc[i] == 'Deposit':
                self.dfcurve.loc[self.dfcurve.index[i],'ZeroRate'] = \
                        (1 / self.dfcurve['CumYearFraction'].iloc[i]) * \
                         np.log([1.0 + self.dfcurve['SwapRate'].iloc[i] * \
                                self.dfcurve['CumYearFraction'].iloc[i]])
            elif self.dfcurve['Type'].iloc[i] == 'EuroDollarFuture':
                rate_continuous = 0.0
                rate_continuous = 4 * np.log([1.0 + self.dfcurve['SwapRate'].iloc[i] * \
                                              self.dfcurve['YearFraction'].iloc[i]])
                self.dfcurve.loc[self.dfcurve.index[i], 'ZeroRate'] = \
                        (rate_continuous * self.dfcurve['YearFraction'].iloc[i] + \
                        self.dfcurve['ZeroRate'].iloc[i-1] * self.dfcurve['CumYearFraction'].iloc[i-1]) / \
                            self.dfcurve['CumYearFraction'].iloc[i]
            else:
                sumproduct = 0.0     
                    
                if self.dfcurve['Type'].iloc[i] == 'Swap':
                    frequency = self.dfcurve['Frequency'].iloc[i]
                    term = int(self.dfcurve.index[i][:-1])
                    swap_year_fractions = self._SwapYearFractions_(frequency,term)
                    # set up interpolation object
                    x = pd.Series(self.dfcurve['CumYearFraction'][:i])
                    y = pd.Series(self.dfcurve['ZeroRate'][:i])
                    zero_tck = interpolate.splrep(x,y)
                    
                for swap_yf in swap_year_fractions:
                    zero_rate = 0.0
                    zero_rate = interpolate.splev(swap_yf, zero_tck)
                    sumproduct = sumproduct + (self.dfcurve['SwapRate'].iloc[i] / 2.0) * \
                                 np.exp(-zero_rate * swap_yf)
               
                self.dfcurve.loc[self.dfcurve.index[i], 'ZeroRate'] = (-1 * np.log((1.0 - sumproduct) / \
                            (1.0 + self.dfcurve['SwapRate'].iloc[i] / 2.0))) / \
                            self.dfcurve['CumYearFraction'].iloc[i]
                
        fileout = "yieldcurve.xlsx"
        
self.dfcurve.to_excel(fileout, sheet_name='yieldcurve', index=True)    


def _DiscountFactors_(self):
        for i in range(len(self.dfcurve)):
            rate_i = self.dfcurve['SwapRate'].iloc[i]
            yearfraction_i = self.dfcurve['YearFraction'].iloc[i]
            cumyearfraction_i = self.dfcurve['CumYearFraction'].iloc[i]
           
 self.dfcurve.loc[self.dfcurve.index[i], 'DiscountFactor'] = np.exp(-rate_i * cumyearfraction_i)




                