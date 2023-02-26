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