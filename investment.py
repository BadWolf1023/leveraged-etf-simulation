from collections import defaultdict
from common import DAYS_PER_YEAR, STARTING_INVESTMENT_AMOUNT, DECREASE_LEVERAGE_AT_YEAR_END,YEAR_END_DECREASE
import math
from datetime import datetime, date

class AllMoneyLost(Exception):
    pass

class Investment():
    def __init__(self, start_index, end_index, security_historical_data, leverage_ratio):
        self.start_date = security_historical_data[start_index].date
        self.end_date = security_historical_data[end_index].date
        self.start_investment = STARTING_INVESTMENT_AMOUNT
        self.leverage_ratio = leverage_ratio
        self.compute_return(start_index, end_index, security_historical_data)

    def is_new_year(self, cur_date:date, previous_date:date):
        if previous_date is None:
            return False
        return cur_date.year > previous_date.year

    def should_charge_interest(self, cur_date, previous_date):
        return self.is_new_year(cur_date, previous_date)

    def charge_interest(self, first_date, previous_date, cur_date, current_investment_amount):
        if previous_date.year == first_date.year: #Charge proportional interest for first year
            proportional_interest = YEAR_END_DECREASE * self.get_fractional_year_from_end(first_date)
            return round(current_investment_amount * (1 - proportional_interest), 2)
        elif cur_date.year > previous_date.year: #Charge interest for full year - it is not a partial first year, and the year did change
            return round(current_investment_amount * (1 - YEAR_END_DECREASE), 2)
        else: #Charge interest for partial final year
            proportional_interest = YEAR_END_DECREASE * self.get_fractional_year(cur_date)
            return round(current_investment_amount * (1 - proportional_interest), 2)


        


    def compute_return(self, start_index, end_index, security_historical_data):
        current_investment_amount = self.start_investment
        first_date = None
        previous_date = None
        for daily_data in security_historical_data[start_index:end_index+1]:
            if first_date is None:
                first_date = daily_data.date

            current_investment_amount *= 1 + (daily_data.ratio_change * self.leverage_ratio)
            current_investment_amount = round(current_investment_amount, 2)
            
            if DECREASE_LEVERAGE_AT_YEAR_END and self.leverage_ratio > 1.0 and self.should_charge_interest(daily_data.date, previous_date):
                current_investment_amount = self.charge_interest(first_date, previous_date, daily_data.date, current_investment_amount)

            if current_investment_amount <= 0.0:
                raise AllMoneyLost(f"If you see this exception, this leveraged ETF ceased operations because it dropped to 0. You lost all your money on {daily_data.date} for this investment:\n{str(self)}")

            previous_date = daily_data.date

        if DECREASE_LEVERAGE_AT_YEAR_END and self.leverage_ratio > 1.0:
            current_investment_amount = self.charge_interest(first_date, previous_date, daily_data.date, current_investment_amount)

        self.end_investment = current_investment_amount
        self.total_return_dollars = round(self.end_investment - self.start_investment, 2)
        self.total_return_percentage = (self.total_return_dollars / self.start_investment) * 100
        self.annualized_return = self.get_annualized_return()

    #annualized rate of return (%) = [[((price of security at exit)/(price of security at entry)) ^ (1 / number of years security is held)] - 1] * 100
    def get_annualized_return(self):
        
        number_of_years_invested = ((self.end_date - self.start_date).days)/DAYS_PER_YEAR
        final_ratio = self.end_investment / self.start_investment
        annualized_ratio = final_ratio ** (1 / number_of_years_invested)
        annualized_percentage = (annualized_ratio - 1) * 100
        return annualized_percentage

    def get_fractional_year(self, date):
        start_of_year = datetime(date.year, 1, 1).date()
        fraction_of_year = (date - start_of_year).days / DAYS_PER_YEAR
        return fraction_of_year

    def get_fractional_year_from_end(self, date):
        end_of_year = datetime(date.year, 12, 31).date()
        fraction_of_year = (end_of_year - date).days / DAYS_PER_YEAR
        return fraction_of_year

    def _convert_to_scalar_year(self, date):
        start_of_year = datetime(date.year, 1, 1).date()
        fraction_of_year = (date - start_of_year).days / DAYS_PER_YEAR
        return date.year + fraction_of_year
        

    def get_scalar_start_year(self):
        return self._convert_to_scalar_year(self.start_date)

    def get_scalar_end_year(self):
        return self._convert_to_scalar_year(self.end_date)
        
        
        

    def __str__(self):
        return f"""Start date: {self.start_date}
End date:   {self.end_date}
Original Investment:   ${self.start_investment}
Ratio:  {self.leverage_ratio}"""

    def get_printable(self):
        return f"""Start date: {self.start_date}
End date:   {self.end_date}
Ratio:  {self.leverage_ratio}
Original Investment:   ${self.start_investment:.2f}
End Value: ${self.end_investment:.2f}
Total % Return: {round(self.total_return_percentage, 2)}%
Annualized return: {round(self.annualized_return, 2)}%"""




class InvestmentsStats():
    def __init__(self, leverage_ratio:float):
        self.leverage_ratio = leverage_ratio
        self.annualized_returns = []
        self.total_gains = []
        self.total_percentage_returns = []
        self.was_largest_gain_list = []
        self.gained_more_than_1_ratio_list = []
        self.start_years = []
        self.end_years = []
        self.investment_periods = []

    
    def add_investment_results(self, investment:Investment, was_largest_gain, gained_more_than_1_ratio):
        assert(investment.leverage_ratio == self.leverage_ratio)
        self.annualized_returns.append(investment.annualized_return)
        self.total_gains.append(investment.total_return_dollars)
        self.total_percentage_returns.append(investment.total_return_percentage)
        self.was_largest_gain_list.append(was_largest_gain)
        self.gained_more_than_1_ratio_list.append(gained_more_than_1_ratio)
        scalar_start_year = investment.get_scalar_start_year()
        scalar_end_year = investment.get_scalar_end_year()
        self.start_years.append(scalar_start_year)
        self.end_years.append(scalar_end_year)
        self.investment_periods.append(scalar_end_year-scalar_start_year)

    def avg_start_year(self):
        return round((sum(self.start_years) / len(self.start_years)), 2)
    def avg_end_year(self):
        return round((sum(self.end_years) / len(self.end_years)), 2)
    def avg_investment_time(self):
        return round((sum(self.investment_periods) / len(self.investment_periods)), 2)


    def percentage_of_time_gained_larger_than_1(self):
        return round((sum(self.gained_more_than_1_ratio_list) / len(self.gained_more_than_1_ratio_list))*100, 2)
    def num_times_gained_larger_than_1(self):
        return round(sum(self.gained_more_than_1_ratio_list), 2)

    def percentage_of_time_was_largest_gain(self):
        return round((sum(self.was_largest_gain_list) / len(self.was_largest_gain_list))*100, 2)
    
    def num_times_was_largest_gain(self):
        return round(sum(self.was_largest_gain_list), 2)

    def average_gain(self) -> float:
        return round(sum(self.total_gains) / len(self.total_gains), 2)
    def worst_gain(self) -> float:
        return round(min(self.total_gains), 2)
    def best_gain(self) -> float:
        return round(max(self.total_gains), 2)

    def average_overall_return(self) -> float:
        return round(sum(self.total_percentage_returns) / len(self.total_percentage_returns), 2)
    def worst_overall_return(self) -> float:
        return round(min(self.total_percentage_returns), 2)
    def best_overall_return(self) -> float:
        return round(max(self.total_percentage_returns), 2)

    def average_annualized_return(self) -> float:
        return round(sum(self.annualized_returns) / len(self.annualized_returns), 3)
    def worst_annualized_return(self) -> float:
        return round(min(self.annualized_returns), 2)
    def best_annualized_return(self) -> float:
        return round(max(self.annualized_returns), 2)