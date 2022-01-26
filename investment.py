"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */
 """
from common import DAYS_PER_YEAR, INCLUDE_DIVIDENDS, STARTING_INVESTMENT_AMOUNT, CHARGE_ETF_EXPENSES, dividend_cost_data
from datetime import datetime, date


class AllMoneyLost(Exception):
    pass

class Investment():
    def __init__(self, start_index, end_index, security_historical_data, leverage_ratio):
        self.start_index = start_index
        self.end_index = end_index
        self.security_historical_data = security_historical_data
        self.start_date = security_historical_data[start_index].date
        self.end_date = security_historical_data[end_index].date
        # print(f"{self.start_date} to {self.end_date}")
        self.start_investment = STARTING_INVESTMENT_AMOUNT
        self.leverage_ratio = leverage_ratio

    def is_new_year(self, cur_date:date, previous_date:date):
        if previous_date is None:
            return False
        return cur_date.year > previous_date.year

    def is_full_year(self, first_date, previous_date, cur_date):
        if previous_date.year == first_date.year: # Case 1 is first year
            return False
        elif cur_date.year > previous_date.year: # Case 2 is full year
            return True
        else: # Case 3 is final year (not full)
            return False

    def after_charges_and_dividends(self, first_date: date, previous_date: date, cur_date: date, current_investment_amount: float, leverage: float):
        prorated_change = 1
        year = None
        if previous_date.year == first_date.year: # Prorated change for first year
            prorated_change = self.get_fractional_year_from_end(first_date)
            year = first_date.year
        elif cur_date.year > previous_date.year: # No prorate. Full year - it is not a partial first year, and the year did change
            prorated_change = 1
            year = previous_date.year
        else: #prorate change for partial final year
            prorated_change = self.get_fractional_year(cur_date)
            year = cur_date.year

        change = 0
        if CHARGE_ETF_EXPENSES:
            print(f"Annual cost for {year} @ {leverage} leverage: {dividend_cost_data.get_annual_cost(year, leverage)}")
            change -= dividend_cost_data.get_annual_cost(year, leverage)
        if INCLUDE_DIVIDENDS:
            print(f"Annual dividend for {year} @ {leverage} leverage: {dividend_cost_data.get_annual_dividend(year, leverage)}")
            change += dividend_cost_data.get_annual_dividend(year, leverage)
        final_change_ratio = 1 + (change * prorated_change)
        return round(current_investment_amount * final_change_ratio, 2)


    def compute_return(self):
        '''Returns self for easy chaining'''
        current_investment_amount = self.start_investment
        first_date = None
        previous_date = None
        for daily_data in self.security_historical_data[self.start_index:self.end_index+1]:
            if first_date is None:
                first_date = daily_data.date

            current_investment_amount *= 1 + (daily_data.ratio_change * self.leverage_ratio)
            current_investment_amount = round(current_investment_amount, 2)
            
            if self.is_new_year(daily_data.date, previous_date):
                current_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, current_investment_amount, self.leverage_ratio)

            if current_investment_amount <= 0.0:
                raise AllMoneyLost(f"If you see this exception, this leveraged ETF ceased operations because it dropped to 0. You lost all your money on {daily_data.date} for this investment:\n{str(self)}")

            previous_date = daily_data.date

        
        current_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, current_investment_amount, self.leverage_ratio)
        self.end_investment = current_investment_amount
        self.total_return_dollars = round(self.end_investment - self.start_investment, 2)
        self.total_return_ratio = round((self.total_return_dollars / self.start_investment), 5)
        self.CAGR = self.get_CAGR_ratio()
        return self

    #CAGR ratio = [[((price of security at exit)/(price of security at entry)) ^ (1 / number of years security is held)] - 1]
    def get_CAGR_ratio(self):
        number_of_years_invested = ((self.end_date - self.start_date).days)/DAYS_PER_YEAR
        final_ratio = self.end_investment / self.start_investment
        CAGR_ratio = final_ratio ** (1 / number_of_years_invested)
        return CAGR_ratio - 1

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

    def get_leverage_ratio_str(self) -> str:
        return str(self.leverage_ratio)
        
        
        

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
Total Return: {self.total_return_ratio:.2%}
CAGR: {self.CAGR:.2%}"""


class InvestmentSplitLeverage(Investment):
    def __init__(self, start_index, end_index, security_historical_data, leverage_ratio, real_large_leverage, real_small_leverage=None):
        super().__init__(start_index, end_index, security_historical_data, leverage_ratio)
        self.real_large_leverage = real_large_leverage 
        self.real_small_leverage = 1.0 if real_small_leverage is None else real_small_leverage

    def compute_return(self):
        '''Returns self for easy chaining'''
        if not self.can_split_weights():
            super().compute_return()
            return self

        (low_leverage, low_leverage_weight), (high_leverage, high_leverage_weight) = self.get_weighted_leverage_split()
        low_leverage_investment_amount = round(self.start_investment * low_leverage_weight, 2)
        high_leverage_investment_amount = round(self.start_investment * high_leverage_weight, 2)
        first_date = None
        previous_date = None
        for daily_data in self.security_historical_data[self.start_index:self.end_index+1]:
            if first_date is None:
                first_date = daily_data.date

            low_leverage_investment_amount *= 1 + (daily_data.ratio_change * low_leverage)
            low_leverage_investment_amount = round(low_leverage_investment_amount, 2)
            high_leverage_investment_amount *= 1 + (daily_data.ratio_change * high_leverage)
            high_leverage_investment_amount = round(high_leverage_investment_amount, 2)
            
            if self.is_new_year(daily_data.date, previous_date):
                low_leverage_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, low_leverage_investment_amount, low_leverage)
                high_leverage_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, high_leverage_investment_amount, high_leverage)

            if (low_leverage_investment_amount + high_leverage_investment_amount) <= 0.0:
                raise AllMoneyLost(f"If you see this exception, this leveraged ETF ceased operations because it dropped to 0. You lost all your money on {daily_data.date} for this investment:\n{str(self)}")

            previous_date = daily_data.date

        low_leverage_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, low_leverage_investment_amount, low_leverage)
        high_leverage_investment_amount = self.after_charges_and_dividends(first_date, previous_date, daily_data.date, high_leverage_investment_amount, high_leverage)
        self.end_investment = round(low_leverage_investment_amount + high_leverage_investment_amount, 2)
        self.total_return_dollars = round(self.end_investment - self.start_investment, 2)
        self.total_return_ratio = round((self.total_return_dollars / self.start_investment), 5)
        self.CAGR = self.get_CAGR_ratio()
        return self

    def can_split_weights(self):
        (low_leverage, low_leverage_weight), (high_leverage, high_leverage_weight) = self.get_weighted_leverage_split()
        return low_leverage_weight > 0.0 and high_leverage_weight > 0.0

    def get_weighted_leverage_split(self):
        # s = smaller leverage to use
        # b = larger leverage to use
        # y = weight of larger leverage
        # x = weight of smaller leverage
        # v = actual leverage ratio
        # At the time the equation needs to be solved, s, b, and v will be known constants
        # x + y = 1
        # s*x + b*y = v
        v = self.leverage_ratio
        s = self.real_small_leverage
        b = self.real_large_leverage
        # x = 1 - y
        # s*(1 - y) + b*y = v
        # s - s*y + b*y = v
        # (b - s)*y + s = v
        # (b - s)*y = v - s
        # y = (v - s)/(b - s)
        # y can be solved. Finding x is trivial now.
        y = (v - s)/(b - s)
        y = round(y, 8)
        x = 1 - y
        x = round(x, 8)
        return (s, x), (b, y)

    def get_leverage_ratio_str(self) -> str:
        if not self.can_split_weights():
            return super().get_leverage_ratio_str()
        (low_leverage, low_leverage_weight), (high_leverage, high_leverage_weight) = self.get_weighted_leverage_split()
        #print(high_leverage_weight)
        return f"{self.leverage_ratio} ({low_leverage_weight:.1%} {low_leverage}, {high_leverage_weight:.1%} {high_leverage})"







class InvestmentsStats():
    def __init__(self, leverage_ratio, leverage_ratio_str: str):
        self.leverage_ratio = leverage_ratio
        self.leverage_ratio_str = leverage_ratio_str
        self.CAGR_ratios = []
        self.total_dollar_returns = []
        self.total_return_ratios = []
        self.was_largest_return_list = []
        self.returned_more_than_1_ratio_list = []
        self.start_dates = []
        self.end_dates = []
        self.start_years = []
        self.end_years = []
        self.investment_periods = []

    def num_investments(self) -> int:
        return len(self.CAGR_ratios)

    def get_leverage_ratio_str(self) -> str:
        return self.leverage_ratio_str
        
    def add_investment_results(self, investment:Investment, was_largest_return, returned_more_than_1_ratio):
        assert(investment.leverage_ratio == self.leverage_ratio)
        assert(investment.get_leverage_ratio_str() == self.get_leverage_ratio_str())
        self.CAGR_ratios.append(investment.CAGR)
        self.total_dollar_returns.append(investment.total_return_dollars)
        self.total_return_ratios.append(investment.total_return_ratio)
        self.was_largest_return_list.append(was_largest_return)
        self.returned_more_than_1_ratio_list.append(returned_more_than_1_ratio)
        scalar_start_year = investment.get_scalar_start_year()
        scalar_end_year = investment.get_scalar_end_year()
        self.start_years.append(scalar_start_year)
        self.start_dates.append(investment.start_date)
        self.end_years.append(scalar_end_year)
        self.end_dates.append(investment.end_date)
        self.investment_periods.append(scalar_end_year-scalar_start_year)

    def avg_start_year(self):
        return round((sum(self.start_years) / len(self.start_years)), 2)
    def avg_end_year(self):
        return round((sum(self.end_years) / len(self.end_years)), 2)
    def avg_investment_time(self):
        return round((sum(self.investment_periods) / len(self.investment_periods)), 2)


    def returned_more_than_leverage_1_frequency(self):
        return sum(self.returned_more_than_1_ratio_list) / len(self.returned_more_than_1_ratio_list)
    
    def returned_more_than_leverage_1_times(self):
        return sum(self.returned_more_than_1_ratio_list)

    def was_largest_return_frequency(self):
        return sum(self.was_largest_return_list) / len(self.was_largest_return_list)
    
    def was_largest_return_times(self):
        return sum(self.was_largest_return_list)



    # ==== Return Dollars Functions ====
    def average_dollar_return(self) -> float:
        return sum(self.total_dollar_returns) / len(self.total_dollar_returns)

    def worst_dollar_return(self) -> float:
        return min(self.total_dollar_returns)

    def best_dollar_return(self) -> float:
        return max(self.total_dollar_returns)

    def worst_dollar_return_index(self):
        return self.total_dollar_returns.index(self.worst_dollar_return())
    
    def best_dollar_return_index(self):
        return self.total_dollar_returns.index(self.best_dollar_return())


    # ==== Return Ratio Functions ====
    def average_return_ratio(self) -> float:
        return sum(self.total_return_ratios) / len(self.total_return_ratios)
    
    def worst_return_ratio(self) -> float:
        return min(self.total_return_ratios)
    
    def best_return_ratio(self) -> float:
        return max(self.total_return_ratios)
    
    def worst_return_index(self):
        return self.total_return_ratios.index(self.worst_return_ratio())
    
    def best_return_index(self):
        return self.total_return_ratios.index(self.best_return_ratio())



    # ==== CAGR Functions ====
    def average_CAGR(self) -> float:
        return sum(self.CAGR_ratios) / len(self.CAGR_ratios)

    def worst_CAGR(self) -> float:
        return min(self.CAGR_ratios)

    def best_CAGR(self) -> float:
        return max(self.CAGR_ratios)

    def worst_CAGR_index(self):
        return self.CAGR_ratios.index(self.worst_CAGR())

    def best_CAGR_index(self):
        return self.CAGR_ratios.index(self.best_CAGR())

    def avg_CAGR_when_less_than(self, threshold: float):
        cagr_ratios_below_threshold = list(filter(lambda x: x < threshold, self.CAGR_ratios))
        if len(cagr_ratios_below_threshold) == 0:
            return f"N/A (none below {threshold:.2%})"
        return sum(cagr_ratios_below_threshold) / len(cagr_ratios_below_threshold)

    def avg_CAGR_when_greater_than(self, threshold: float):
        cagr_ratios_above_threshold = list(filter(lambda x: x > threshold, self.CAGR_ratios))
        if len(cagr_ratios_above_threshold) == 0:
            return f"N/A (none above {threshold:.2%})"
        return sum(cagr_ratios_above_threshold) / len(cagr_ratios_above_threshold)

    def CAGR_less_than_frequency(self, threshold: float):
        return len(list(filter(lambda x: x < threshold, self.CAGR_ratios))) / len(self.CAGR_ratios)
        
    def CAGR_greater_than_frequency(self, threshold: float):
        return (len(list(filter(lambda x: x > threshold, self.CAGR_ratios))) / len(self.CAGR_ratios))

    @staticmethod
    def get_tab_printed_overview_headers(cagr_threshold=0.0, cagr_threshold_stats=True, return_threshold_stats=True):
        cagr_threshold_headers = [f"Final CAGR < {cagr_threshold:.1%}",
        f"Avg of CAGRs when CAGR < {cagr_threshold:.2%}",
        f"Final CAGR > {cagr_threshold:.1%}",
        f"Avg of CAGRs when CAGR > {cagr_threshold:.2%}"]

        all_return_threshold_headers = [f"Final return < {t/4:.0%}" for t in range(-3, 1)]
        all_return_threshold_headers.extend([f"Final return > {t/4:.0%}" for t in range(5)])
        all_return_threshold_headers.extend([f"Final return > {t:.0%}" for t in range(2, 6)])

        headers = ["Leverage Ratio",
        "# of times largest return",
        f"Return is largest return",
        "Average of all returns ($)",
        "Best return ($)",
        "Worst return ($)",
        "Average of all returns (%)",
        "Best return (%)",
        "Worst return (%)",
        "Avg of CAGRs",
        "Best CAGR",
        "Worst CAGR",
        f"Final CAGR > 1.0 leverage's CAGR",
        "# of times > 1.0 leverage"]

        headers_2 = [
        "Avg start year (same for all)",
        "Avg end year (same for all)",
        "Avg investment period (same for all)"
        ]

        final_data = headers
        final_data.extend((cagr_threshold_headers if cagr_threshold_stats else []))
        final_data.extend((all_return_threshold_headers if return_threshold_stats else []))
        final_data.extend(headers_2)
        return "\t".join(final_data)

    def return_beyond_threshold_times(self, threshold_percentage:float, below=True):
        filter_func = (lambda x: x < threshold_percentage) if below else (lambda x: x > threshold_percentage)
        return len(list(filter(filter_func, self.total_return_ratios)))


    def get_tab_printed_overview_data(self, cagr_threshold=0.0, cagr_threshold_stats=True, return_threshold_stats=True):
        cagr_avg_when_less_than_threshold = self.avg_CAGR_when_less_than(cagr_threshold)
        cagr_avg_when_more_than_threshold = self.avg_CAGR_when_greater_than(cagr_threshold)
        cagr_threshold_data = [f"{self.CAGR_less_than_frequency(cagr_threshold):.2%}",
        f"{cagr_avg_when_less_than_threshold:.2%}" if isinstance(cagr_avg_when_less_than_threshold, float) else f"{cagr_avg_when_less_than_threshold}",
        f"{self.CAGR_greater_than_frequency(cagr_threshold):.2%}",
        f"{cagr_avg_when_more_than_threshold:.2%}" if isinstance(cagr_avg_when_more_than_threshold, float) else f"{cagr_avg_when_more_than_threshold}"]

        below_return_threshold_percentages = [f"{self.return_beyond_threshold_times(t/4, below=True) / self.num_investments():.2%}" for t in range(-3, 1)]
        above_return_threshold_percentages = [f"{self.return_beyond_threshold_times(t/4, below=False) / self.num_investments():.2%}" for t in range(5)]
        above_return_threshold_percentages.extend([f"{self.return_beyond_threshold_times(t, below=False) / self.num_investments():.2%}" for t in range(2, 6)]) 
        all_return_threshold_percentages = below_return_threshold_percentages + above_return_threshold_percentages


        data = [f"{self.get_leverage_ratio_str()}",
        f"{self.was_largest_return_times()}",
        f"{self.was_largest_return_frequency():.2%}",
        f"{self.average_dollar_return():.2f}",
        f"{self.best_dollar_return():.2f}",
        f"{self.worst_dollar_return():.2f}",
        f"{self.average_return_ratio():.2%}",
        f"{self.best_return_ratio():.2%}",
        f"{self.worst_return_ratio():.2%}",
        f"{self.average_CAGR():.2%}",
        f"{self.best_CAGR():.2%}",
        f"{self.worst_CAGR():.2%}",
        f"{self.returned_more_than_leverage_1_frequency():.0%}",
        f"{self.returned_more_than_leverage_1_times()}"]

        data_2 = [
        f"{self.avg_start_year():.2f}",
        f"{self.avg_end_year():.2f}",
        f"{self.avg_investment_time():.2f}"
        ]

        final_data = data
        final_data.extend((cagr_threshold_data if cagr_threshold_stats else []))
        final_data.extend((all_return_threshold_percentages if return_threshold_stats else []))
        final_data.extend(data_2)
        return "\t".join(final_data)

    @staticmethod
    def get_tab_printed_invesment_headers(is_CAGR=False):
        return """Leverage Ratio\tCAGR\tTotal Return ($)\tTotal Return (%)\tWas largest return for ratios\tReturned more than 1.0 ratio\tStart Date\tEnd Date\tInvestment Period (yrs)"""
        
    def get_tab_printed_investment(self, index):
        if index < 0 or index >= len(self.CAGR_ratios):
            raise IndexError(f"Index {index} not in range of recorded investments (0 to {len(self.CAGR_ratios)-1})")
        return f"""{self.get_leverage_ratio_str()}\t{self.CAGR_ratios[index]:.2%}\t{self.total_dollar_returns[index]:.2f}\t{self.total_return_ratios[index]:.2%}\t{"Yes" if self.was_largest_return_list[index] else "No"}\t{"Yes" if self.returned_more_than_1_ratio_list[index] else "No"}\t{self.start_dates[index]}\t{self.end_dates[index]}\t{self.investment_periods[index]:.2f}"""
    
    def get_printable_index_information(self, index):
        if index < 0 or index >= len(self.CAGR_ratios):
            raise IndexError(f"Index {index} not in range of recorded investments (0 to {len(self.CAGR_ratios)-1})")
        return f"""Leverage Ratio: {self.leverage_ratio}
CAGR: {self.CAGR_ratios[index]:.0%}
Total Return ($): ${self.total_dollar_returns[index]:.2f}
Total Return (%): {self.total_return_ratios[index]:.2%}
Was largest return for ratios: {"Yes" if self.was_largest_return_list[index] else "No"}
Returned more than 1.0 ratio:  {"Yes" if self.returned_more_than_1_ratio_list[index] else "No"}
Start: {self.start_dates[index]}
End:  {self.end_dates[index]}
Investment Period: {self.investment_periods[index]:.2f} yrs
"""
