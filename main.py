"""
Leveraged ETF simulator

Much misinformation surrounds holding leveraged ETFs long term. This simulation attempts to use real data to simulate a 2x leveraged ETF outcome and a 3x leveraged ETF outcome compared with the underlying index.

It is known that volatility of a security can result in decay. While this may be true, my hypothesis is that the affect of the decay is frequently overplayed and investors shy away from an opportunity that
could generate significant returns, returns that I suspect would far outpace the rate of decay.

While decay may exist in times of volatility where the security price remains constant, risk can be mitigated by investing in major indexes. Major U.S. indexes have historically gone up over their lifetime, such as the DJIA which has gone up over the past 100 years.

My hypothesis is that a leverage of 1.9x, contrary to conventional investment wisdom, will result in much higher gains when invested in ETFs that accurately track (>.99) a major U.S. index.

The following assumptions are made:
1. The leveraged ETF is held over a long period of time, that is, more than 2 years, but no more than 20 years. This is a study of holding leveraged ETFs long term, so they should be held long term. The amount of time the ETF is held should be randomized since investors frequently struggle to time an exit perfectly.*
2. It is assumed that investors cannot predict the future of an index's price. Therefore, entries into the market should be randomly selected.*
3. Dividends are not reinvested. This makes certain calculations difficult. Generally speaking though, leveraged ETFs do not offer as good of a dividend as a normal ETF. Eg compare DIA's 1.6% dividend to UDOW's .2% dividend.
4. There are no adjustments for inflation because the comparison is not against cash, but rather is against an index.
5. Taxes are ignored. Various ETFs are structured differently, resulting in different tax repercussions for the investor. Note that taxes can be due as frequently as a quarterly basis depending on the structure of the ETF,
and taxes rates can vary (long term capital gains taxes, corporate taxes, and individual taxes).
6. Yearly management fees can be included in the calculation in the common.py file. A suggested 1% management fee would match most leveraged ETFs that track major U.S. indexes (eg UDOW, TQQQ, ... all charge .95%). If the leverage of the investment is 1.0, the leveraged ETF management fee in common.py will not apply.

*I am aware that different expertise, knowledge, metrics, and other factors can increase (or decrease) the odds of a well timed entry or exit, but because the average investor's entries and exits are quite random in relation to
the short term (and sometimes even long term) outcome of the security, a random entry and exit seem to simulate actual investor behaviour the best.



The experiment will go as follows:
- 1000 experiments will be ran with random entry and random exit points, with the exit point being between 2 years and 20 years of the entry point.
- The annualized rate of return will be recorded for that period on both a leveraged ETF and a normal ETF.
- The results will show the average annualized return of those 1000 experiments, worst return, and best return, along with other data.



The formula for calculating an annualized return based off a given period of time is:
annualized rate of return (%) = [[((price of security at entry)/(price of security at exit)) ^ (1 / number of years security is held)] - 1] * 100


OUTCOME:
- Based on the indexes for the Dow Jones (1900 to 2021), NASDAQ-100 (1985 - 2021), and S&P500 (1900 to 2021), a leverage of 1.0 does not yield the highest annualized rate over the 1000 random long term entries and exits.
- While the exact optimal leverage for each varies, a leverage of 2.7 yields the optimal annualized average rate of return for all 3 indexes.
- A lower leverage (1.5-2.2) frequently outperforms the index at a much higher frequency, though the annualized rate of return is lower. Therefore, you could significantly reduce the chances of the normal index outperforming your investment
by investing at a lower leverage if that is the concern.
- A leverage of 3.8-3.9 generates the largest average returns overall.
- It makes sense that 2.7 is the optimal leverage for maximum annualized rate of return. Thisnicely balances both the high risk/high payoff/high loss of the large average returns of 3.8 leverage,
and the safe odds of outperforming the 1.0 index at a 1.5-2.2 leverage.


DISCLAIMER: I am not offering investment advice. I am obviously not responsible for your investment outcomes. I am simulating these purely out of curiosity. Investing in leveraged ETFs, ETFs, or other securities, can result in loss of money (sometimes all of it) and debt.
"""
from collections import defaultdict
import csv
from datetime import date, datetime, timedelta
import random
from asset_data import DailyAssetData

from typing import DefaultDict, List
from common import reversed_enumerate, DAYS_PER_YEAR
from investment import Investment, InvestmentsStats

file_names = ["dji_d.csv", "spx_d.csv", "ndx_d.csv"]
security_historical_data:List[DailyAssetData] = []

MIN_INVESTMENT_YEARS = 2
MAX_INVESTMENT_YEARS = 20



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

def get_max_date_index(max_date:date=None):
    if max_date is None:
        return len(security_historical_data) - 1
    for index, day in reversed_enumerate(security_historical_data):
        if day.date <= max_date:
            return index

def choose_random_date(min_date=None, max_date=None):
    min_index = get_min_date_index(min_date)
    max_index = get_max_date_index(max_date)
        
    if min_index > max_index:
        raise IncorrectUsage("Your min_date must be before your max_date. If you're sure it is, your CSV must be sorted backwards.")

    return random.randint(min_index, max_index)

def hint_typed_dd() -> List[Investment]:
    return []

def run_simulation(num_times=1000, leverage_ratios=[1.0, 2.0, 3.0]) -> DefaultDict[float, hint_typed_dd]:
    if 1.0 not in leverage_ratios:
        leverage_ratios.append(1.0)

    results = defaultdict(hint_typed_dd)
    max_start_date = security_historical_data[-1].date - timedelta(days=int(round(MIN_INVESTMENT_YEARS*DAYS_PER_YEAR, 0)))
    for i in range(num_times):
        min_index = choose_random_date(max_date=max_start_date)
        min_end_date = security_historical_data[min_index].date + timedelta(days=int(round(MIN_INVESTMENT_YEARS*DAYS_PER_YEAR, 0)))
        max_end_date = security_historical_data[min_index].date + timedelta(days=int(round(MAX_INVESTMENT_YEARS*DAYS_PER_YEAR, 0)))
        max_index = choose_random_date(min_date=min_end_date, max_date=max_end_date)

        
        for leverage_ratio in leverage_ratios:
            cur_investment = Investment(min_index, max_index, security_historical_data, leverage_ratio)
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
        - Annualized return: {round(leverage_ratio_results.annualized_return, 2)}%
        - Total Gain: ${leverage_ratio_results.total_return_dollars:.2f}"""
    return result_text


def print_results(simulation_results:DefaultDict[float, hint_typed_dd]) -> None:
    leverage_results = {leverage_ratio:InvestmentsStats(leverage_ratio) for leverage_ratio in simulation_results}
    simulation_results = restructure_results(simulation_results)
    
    for period_investment_results in simulation_results:
        #print(get_period_investment_results_str(period_investment_results))
        largest_return_ratio = max(period_investment_results, key=lambda x: x.total_return_dollars).leverage_ratio
        
        for leverage_ratio_results in period_investment_results:
            is_greater_than_1_ratio = leverage_ratio_results.total_return_dollars > list(filter(lambda x: x.leverage_ratio == 1.0, period_investment_results))[0].total_return_dollars
            cur_leverage_ratio = leverage_ratio_results.leverage_ratio
            is_best_ratio = cur_leverage_ratio == largest_return_ratio
            leverage_results[cur_leverage_ratio].add_investment_results(leverage_ratio_results, is_best_ratio, is_greater_than_1_ratio)
    
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
   - Average annualized return: {total_leverage_result.average_annualized_return():.2f}%
   - Best    annualized return: {total_leverage_result.best_annualized_return():.2f}%
   - Worst   annualized return: {total_leverage_result.worst_annualized_return():.2f}%
   - Percentage of time > 1.0: {total_leverage_result.percentage_of_time_gained_larger_than_1():.2f}%
   - Number of times > 1.0:    {total_leverage_result.num_times_gained_larger_than_1():.2f}
   - Average start year:     {total_leverage_result.avg_start_year():.2f} yrs
   - Average end year:       {total_leverage_result.avg_end_year():.2f} yrs
   - Average investment time:{total_leverage_result.avg_investment_time():.2f} yrs

"""

    spreadsheet_formatted_result = "Leverage Ratio\tLargest gain # times\tLargest gain % of time\tAverage gain\tBest gain\tWorst gain\tAverage return\tBest return\tWorst return\tAvg Annualized Return\tBest Annualized Return\tWorst Annualized Return\tPercent of time > 1.0\t# of times > 1.0\tAverage start year\tAverage end year\tAverage investment period\n"
    for leverage_ratio, total_leverage_result in leverage_results.items():
        spreadsheet_formatted_result += f"""{leverage_ratio}\t{total_leverage_result.num_times_was_largest_gain():.2f}\t{total_leverage_result.percentage_of_time_was_largest_gain()/100:.4f}\t{total_leverage_result.average_gain():.2f}\t{total_leverage_result.best_gain():.2f}\t{total_leverage_result.worst_gain():.2f}\t{total_leverage_result.average_overall_return()/100:.4f}\t{total_leverage_result.best_overall_return()/100:.4f}\t{total_leverage_result.worst_overall_return()/100:.4f}\t{total_leverage_result.average_annualized_return()/100:.4f}\t{total_leverage_result.best_annualized_return()/100:.4f}\t{total_leverage_result.worst_annualized_return()/100:.4f}\t{total_leverage_result.percentage_of_time_gained_larger_than_1()/100:.4f}\t{total_leverage_result.num_times_gained_larger_than_1()}\t{total_leverage_result.avg_start_year():.2f}\t{total_leverage_result.avg_end_year():.2f}\t{total_leverage_result.avg_investment_time():.2f}
"""
    #print(result)

    print(spreadsheet_formatted_result)
    print()

   


if __name__ == "__main__":
    for file_name in file_names:
        load_data(file_name)
        verify_correctness()
        simulation_results = run_simulation(num_times=1000, leverage_ratios=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0])
        print_results(simulation_results)






















