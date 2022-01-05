"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */

Leveraged ETF simulator

## BACKGROUND:
Much misinformation surrounds holding leveraged ETFs long term. This simulation attempts to use real data to simulate ETF outcomes at different leverages compared with the underlying index.

It is known that volatility of a security can result in decay. While this may be true, my hypothesis is that the affect of the decay is frequently overplayed and investors shy away from an opportunity that could generate significant returns, returns that I suspect would far outpace the rate of decay.

While decay may exist in times of volatility where the security price remains constant, risk can be mitigated by investing in major indexes. Major U.S. indexes have historically gone up over their lifetime, such as the DJIA which has gone up over the past 100 years.

## HYPOTHESIS: 
My hypothesis is that a leverage of 1.9x, contrary to conventional investment wisdom, will result in much higher gains when invested in ETFs that accurately track (>.99) a major U.S. index.

## ASSUMPTIONS AND LIMITATIONS:
The following assumptions are made:
1. The leveraged ETF is held over a long period of time, that is, more than 2 years, but no more than 20 years. This is a study of holding leveraged ETFs long term, so they should be held long term. The amount of time the ETF is held should be randomized since investors frequently struggle to time an exit perfectly.*
2. It is assumed that investors cannot predict the future of an index's price. Therefore, entries into the market should be randomly selected.*
3. Dividends are not reinvested. This makes certain calculations difficult. Generally speaking though, leveraged ETFs do not offer as good of a dividend as a normal ETF. Eg compare DIA's 1.6% dividend to UDOW's .2% dividend.
4. There are no adjustments for inflation because the comparison is not against cash, but rather is against an index.
5. Taxes are ignored. Various ETFs are structured differently, resulting in different tax repercussions for the investor. Note that taxes can be due as frequently as a quarterly basis depending on the structure of the ETF, and taxes rates can vary (long term capital gains taxes, corporate taxes, and individual taxes).
6. Yearly management fees can be included in the calculation in the common.py file. A suggested 1% management fee would match most leveraged ETFs that track major U.S. indexes (eg UDOW, TQQQ, ... all charge .95%). If the leverage of the investment is 1.0, the leveraged ETF management fee in common.py will not apply.

*I am aware that different expertise, knowledge, metrics, and other factors can increase (or decrease) the odds of a well timed entry or exit, but because the average investor's entries and exits are quite random in relation to the short term (and sometimes even long term) outcome of the security, a random entry and exit seem to simulate actual investor behaviour the best.


## Experiment execution:
The experiment will go as follows:
- 1000 experiments will be ran with random entry and random exit points, with the exit point being between 2 years and 20 years of the entry point.
- The compound annual growth rate (CAGR) will be recorded for that period on both a leveraged ETF and a normal ETF.
- The results will show the average CAGR of those 1000 experiments, worst return, and best return, average total return, percentage of time a leverage outperforms the index, along with other data.

The formula for calculating CAGR is:
Compound Annual Growth Rate (%) = [[((price of security at entry)/(price of security at exit)) ^ (1 / number of years security is held)] - 1] * 100


## OUTCOME:
- Based on the indexes for the Dow Jones (1900 to 2021), NASDAQ-100 (1985 - 2021), and S&P500 (1900 to 2021), a leverage of 1.0 does not yield the highest CAGR over the 1000 random long term entries and exits.
- While the exact optimal leverage for each varies, a leverage of 2.7 yields the optimal CAGR average for all 3 indexes.
- A lower leverage (1.5-2.2) frequently outperforms the index at a much higher frequency, though the CAGR average is lower. Therefore, you could significantly reduce the chances of the normal index outperforming your investment by investing at a lower leverage if that is the concern.
- A leverage of 3.8-3.9 generates the largest average returns overall.
- It makes sense that 2.7 is the optimal leverage for maximum CAGR. This nicely balances both the high risk/high payoff/high loss of the large average returns of 3.8 leverage, and the safe odds of outperforming the 1.0 index at a 1.5-2.2 leverage.


## DISCLAIMER:
I am not offering investment advice. I am obviously not responsible for your investment outcomes. I am simulating these purely out of curiosity. Investing in leveraged ETFs, ETFs, or other securities, can result in loss of money (sometimes all of it) and debt.
"""
from collections import defaultdict
import csv
from datetime import date, datetime, timedelta
import random
from asset_data import DailyAssetData

from typing import DefaultDict, List
import common
from investment import Investment, InvestmentsStats


security_historical_data:List[DailyAssetData] = []



class IncorrectUsage(Exception):
    pass

def should_break(csv_line):
    if not isinstance(csv_line, list):
        return True
    if len(csv_line) < 1 or not isinstance(csv_line[0], str) or csv_line[0] == '':
        return True

def load_data(file_name = None):
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)
        previous_day = None
        security_historical_data.clear()
        for r in reader:
            if should_break(r):
                break
            cur_day = DailyAssetData(r, previous_day)
            security_historical_data.append(cur_day)
            previous_day = cur_day

#If we had invested the close amount of the security on the first day, using daily gain and loss percentages,
# we should arrive at the security value today
#Function throws an assertion error if this is not true
def verify_correctness():
    starting_investment = security_historical_data[0].close
    current_investment_amount = starting_investment
    for daily_data in security_historical_data:
        current_investment_amount *= 1 + daily_data.ratio_change
        current_investment_amount = round(current_investment_amount, 2)
    assert(current_investment_amount == security_historical_data[-1].close)


def get_min_date_index(min_date:date=None):
    if min_date is None:
        return 0
    for index, day in enumerate(security_historical_data):
        if day.date >= min_date:
            return index
    raise IncorrectUsage(f"You requested a minimum date of {min_date}, but the csv file's latest date is {day.date} which is before your minimum date.")

def get_max_date_index(max_date:date=None):
    if max_date is None:
        return len(security_historical_data) - 1
    for index, day in common.reversed_enumerate(security_historical_data):
        if day.date <= max_date:
            return index
    raise IncorrectUsage(f"You requested a maximum date of {max_date}, but the csv file's earliest date is {day.date} which is after your maximum date.")

def get_date_index(date:date=None):
    def get_delta(needle_date, cur_date):
        return (needle_date - cur_date).days ** 2

    index_with_lowest_delta = 0
    lowest_delta = get_delta(date, security_historical_data[0].date)
    for index, day in enumerate(security_historical_data):
        cur_delta = get_delta(date, day.date)
        if cur_delta <= lowest_delta:
            lowest_delta = cur_delta
            index_with_lowest_delta = index
    return index_with_lowest_delta

def choose_random_date(min_date=None, max_date=None):
    min_index = get_min_date_index(min_date)
    max_index = get_max_date_index(max_date)
        
    if min_index > max_index:
        raise IncorrectUsage("Your min_date must be before your max_date. If you're sure it is, your CSV must be sorted backwards.")

    return random.randint(min_index, max_index)

def choose_random_length(min_years=common.MIN_INVESTMENT_YEARS, max_years=common.MAX_INVESTMENT_YEARS):
    return timedelta(days= random.randint(round(min_years*common.DAYS_PER_YEAR), round(max_years*common.DAYS_PER_YEAR)) )


def hint_typed_dd() -> List[Investment]:
    return []

def run_simulation(num_times=1000, leverage_ratios=[1.0, 2.0, 3.0]) -> DefaultDict[float, hint_typed_dd]:
    if 1.0 not in leverage_ratios:
        leverage_ratios.append(1.0)

    results = defaultdict(hint_typed_dd)
    for i in range(num_times):
        investment_length = choose_random_length() #Choose random length of time for investment
        min_start_date = max( security_historical_data[0].date, security_historical_data[0].date if common.MINIMUM_START_YEAR is None else datetime(common.MINIMUM_START_YEAR, 1, 1).date() ) #Determine the minimum start date for the investment
        max_start_date = min( security_historical_data[-1].date, security_historical_data[-1].date if common.MAXIMUM_END_YEAR is None else datetime(common.MAXIMUM_END_YEAR, 12, 31).date() ) - investment_length #Determine the maximum start date for the investment, which is the maximum start date minus the investment length
        start_index = choose_random_date(min_date=min_start_date, max_date=max_start_date) #Get the index in security_historical_data of a randomly chosen date between the minimum and maximum start date
        end_date = security_historical_data[start_index].date + investment_length #The end date is simply the investment's start date plus the investment's length
        end_index = get_date_index(end_date) #Get the index in security_historical_data of the trading day that is closest to the end date

        #print(f"{security_historical_data[start_index].date} to {end_date}")
        for leverage_ratio in leverage_ratios:
            cur_investment = Investment(start_index, end_index, security_historical_data, leverage_ratio)
            results[leverage_ratio].append(cur_investment)
    return results

def restructure_results(simulation_results:DefaultDict[float, hint_typed_dd]) -> List[List[Investment]]:
    return [list(r) for r in zip(*simulation_results.values())]


def get_period_investment_results_str(period_investment_results:List[Investment]) -> str:
    result_text = f"""Start date: {period_investment_results[0].start_date}
End date: {period_investment_results[0].end_date}
Original Investment: ${period_investment_results[0].start_investment:.2f}"""
    for leverage_ratio_results in period_investment_results:
        result_text += f"""
    - Ratio:  {leverage_ratio_results.leverage_ratio}
        - End Value: ${leverage_ratio_results.end_investment:.2f}
        - Total % Return: {round(leverage_ratio_results.total_return_percentage, 2)}%
        - CAGR %: {round(leverage_ratio_results.CAGR, 2)}%
        - Total Gain: ${leverage_ratio_results.total_return_dollars:.2f}"""
    return result_text


def print_results(simulation_results:DefaultDict[float, hint_typed_dd], ) -> None:
    leverage_results = {leverage_ratio:InvestmentsStats(leverage_ratio) for leverage_ratio in simulation_results}
    simulation_results = restructure_results(simulation_results)
    
    for period_investment_results in simulation_results:
        # print(get_period_investment_results_str(period_investment_results))
        largest_return_ratio = max(period_investment_results, key=lambda x: x.total_return_dollars).leverage_ratio
        
        for leverage_ratio_results in period_investment_results:
            is_greater_than_1_ratio = leverage_ratio_results.total_return_dollars > list(filter(lambda x: x.leverage_ratio == 1.0, period_investment_results))[0].total_return_dollars
            cur_leverage_ratio = leverage_ratio_results.leverage_ratio
            is_best_ratio = cur_leverage_ratio == largest_return_ratio
            leverage_results[cur_leverage_ratio].add_investment_results(leverage_ratio_results, is_best_ratio, is_greater_than_1_ratio)
    
    
    if common.PRINT_EXTRA_STATS_ON_BEST_WORST:
        best_cagr_text = f"Best CAGR Info:\n{InvestmentsStats.get_tab_printed_invesment_headers()}"
        worst_cagr_text = f"Worst CAGR Info:\n{InvestmentsStats.get_tab_printed_invesment_headers()}"
        worst_return_info_text = f"Worst Overall return Info: \n{InvestmentsStats.get_tab_printed_invesment_headers()}"
        best_return_info_text = f"Best overall return Info: \n{InvestmentsStats.get_tab_printed_invesment_headers()}"
        for leverage_ratio, total_leverage_result in leverage_results.items():
            best_cagr_text += "\n" + total_leverage_result.get_tab_printed_investment(total_leverage_result.best_CAGR_index())
            worst_cagr_text +=  "\n" + total_leverage_result.get_tab_printed_investment( total_leverage_result.worst_CAGR_index())
            worst_return_info_text +=  "\n" + total_leverage_result.get_tab_printed_investment( total_leverage_result.worst_overall_return_index())
            best_return_info_text +=  "\n" + total_leverage_result.get_tab_printed_investment( total_leverage_result.best_overall_return_index())
        print(f"{best_cagr_text}\n\n{worst_cagr_text}\n\n{worst_return_info_text}\n\n{best_return_info_text}\n\n")

    result = ""
    for leverage_ratio, total_leverage_result in leverage_results.items():
        result += f"""Leverage Ratio: {leverage_ratio}
   - Largest gain # times:   {total_leverage_result.num_times_was_largest_gain():.2f}
   - Largest gain % of time: {total_leverage_result.percentage_of_time_was_largest_gain():.2f}%
   - Average Gain: ${total_leverage_result.average_gain():.2f}
   - Best Gain:    ${total_leverage_result.best_gain():.2f}
   - Worst Gain:   ${total_leverage_result.worst_gain():.2f}
   - Average    overall return: {total_leverage_result.average_overall_return():.2f}%
   - Best       overall return: {total_leverage_result.best_overall_return():.2f}%
   - Worst      overall return: {total_leverage_result.worst_overall_return():.2f}%
   - Average CAGR: {total_leverage_result.average_CAGR():.2f}%
   - Best    CAGR: {total_leverage_result.best_CAGR():.2f}%
   - Worst   CAGR: {total_leverage_result.worst_CAGR():.2f}%
   - Percentage of time > 1.0: {total_leverage_result.percentage_of_time_gained_larger_than_1():.2f}%
   - Number of times > 1.0:    {total_leverage_result.num_times_gained_larger_than_1():.2f}
   - Average start year:     {total_leverage_result.avg_start_year():.2f} yrs
   - Average end year:       {total_leverage_result.avg_end_year():.2f} yrs
   - Average investment time:{total_leverage_result.avg_investment_time():.2f} yrs
"""

    spreadsheet_formatted_result = InvestmentsStats.get_tab_printed_overview_headers(cagr_threshold=common.EXTRA_STAT_CAGR_THRESHOLD, cagr_threshold_stats=common.PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD)
    for leverage_ratio, total_leverage_result in leverage_results.items():
        spreadsheet_formatted_result += "\n" + total_leverage_result.get_tab_printed_overview_data(
            cagr_threshold=common.EXTRA_STAT_CAGR_THRESHOLD,
            cagr_threshold_stats=common.PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD
        )
    #print(result)

    print(f"Total results:\n{spreadsheet_formatted_result}\n")

   


if __name__ == "__main__":
    for file_name in common.file_names:
        print(f"File: {file_name}")
        load_data(file_name)
        verify_correctness()
        simulation_results = run_simulation(num_times=common.NUMBER_OF_INVESTMENTS, leverage_ratios=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0])
        
        print_results(simulation_results)






















