"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */
 """
import csv
from dateutil.parser import parse
from typing import Union

file_names = ["dji_d.csv", "spx_d.csv", "ndx_d.csv"]
OUTPUT_FILE_NAME = "results.txt"

DAYS_PER_YEAR = 365.2422
STARTING_INVESTMENT_AMOUNT = 10000

NUMBER_OF_INVESTMENTS = 1
MIN_INVESTMENT_YEARS = 2
MAX_INVESTMENT_YEARS = 4

MINIMUM_START_YEAR = 1960
MAXIMUM_END_YEAR = 2019
PRINT_EXTRA_STATS_ON_BEST_WORST = True
PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD = False
EXTRA_STAT_CAGR_THRESHOLD = .01  # This threshold is used for additional display stats when investment's CAGR is below or above this threshold - not used if PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD is False

PRINT_EXTRA_RETURN_THRESHOLD_STATS = True

PRINT_PROGRESS = True

INCLUDE_DIVIDENDS = True
CHARGE_ETF_EXPENSES = True
LEVERAGED_ETF_EXPENSE_RATIO = .01  # 1%
UNLEVERAGED_ETF_EXPENSE_RATIO = .001  # .1%

USE_REALISTIC_SPLIT_LEVERAGE = True


def reversed_enumerate(collection: list):
    for i in range(len(collection)-1, -1, -1):
        yield i, collection[i]

def should_break(csv_line):
    if not isinstance(csv_line, list):
        return True
    if len(csv_line) < 1 or not isinstance(csv_line[0], str) or csv_line[0] == '':
        return True


class KnownIndexMetaData():
    KNOWN_FILE_NAMES = {"dji_d.csv": "^DJI",
                        "spx_d.csv": "^INX",
                        "ndx_d.csv": "^IXIC"}

    def __init__(self):
        self._file_name = None
        self._load_data()

    def _load_data(self):
        self._known_index_data = {"^DJI": {"file_name": "dji_d.csv",
                                           "dividend_data_file": "./dividends/dji_d_dividends.csv",
                                           "yearly_dividend_ratios": {},
                                           "leverage_data": {1.0: {"symbol": "DIA",
                                                                 "annual_expense_ratio": .0016,
                                                                 "dividend_multiplier": 1.0
                                                                 },
                                                             2.0: {"symbol": "DDM",
                                                                 "annual_expense_ratio": .0095,
                                                                 "dividend_multiplier": .12
                                                                 },
                                                             3.0: {"symbol": "UDOW",
                                                                 "annual_expense_ratio": .0095,
                                                                 "dividend_multiplier": .18
                                                                 }
                                                             }
                                           },
                                  "^INX": {"file_name": "spx_d.csv",
                                           "dividend_data_file": "./dividends/spx_d_dividends.csv",
                                           "yearly_dividend_ratios": {},
                                           "leverage_data": {1.0: {"symbol": "SWPPX",
                                                                 "annual_expense_ratio": .0002,
                                                                 "dividend_multiplier": 1.0
                                                                 },
                                                             2.0: {"symbol": "SPUU",
                                                                 "annual_expense_ratio": .0064,
                                                                 "dividend_multiplier": .15
                                                                 },
                                                             3.0: {"symbol": "UPRO",
                                                                 "annual_expense_ratio": .0091,
                                                                 "dividend_multiplier": .06
                                                                 }
                                                             }
                                           },
                                  "^IXIC": {"file_name": "ndx_d.csv",
                                            "dividend_data_file": .0055,
                                            "yearly_dividend_ratios": .0055,
                                            "leverage_data": {1.0: {"symbol": "VUG",
                                                                  "annual_expense_ratio": .0004,
                                                                  "dividend_multiplier": 1.0
                                                                  },
                                                              2.0: {"symbol": "QLD",
                                                                  "annual_expense_ratio": .0095,
                                                                  "dividend_multiplier": 0
                                                                  },
                                                              3.0: {"symbol": "TQQQ",
                                                                  "annual_expense_ratio": .0095,
                                                                  "dividend_multiplier": 0
                                                                  }
                                                              }
                                            }
                                  }
        for symbol_dividend_data in self._known_index_data.values():
            if not isinstance(symbol_dividend_data["dividend_data_file"], str):
                symbol_dividend_data["yearly_dividend_ratios"] = float(symbol_dividend_data["dividend_data_file"])
            else:
                with open(symbol_dividend_data["dividend_data_file"]) as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    header = next(reader)
                    previous_day = None
                    for r in reader:
                        if should_break(r):
                            break
                        cur_year = parse(r[0]).date().year
                        dividend_ratio = 0.0
                        try:
                            dividend_ratio = float(r[1])
                        except:
                            pass
                        symbol_dividend_data["yearly_dividend_ratios"][cur_year] = dividend_ratio
        
                        
            
                


    def set_file_name(self, file_name: str):
        self._file_name = file_name

    def get_annual_dividend(self, year: int, leverage: Union[int, float]) -> float:        
        if not INCLUDE_DIVIDENDS or self._file_name not in self.KNOWN_FILE_NAMES:
            return 0.0

        leverage = float(leverage)
        if leverage > 3.0:  # Use 3.0 leverage if more than 3.0
            leverage = 3.0
        if leverage < 1.0:  # Use 1.0 leverage if less than 1.0
            leverage = 1.0
        yearly_dividend = 0.0
        annual_dividend_ratios = self._known_index_data[self.KNOWN_FILE_NAMES[self._file_name]]["yearly_dividend_ratios"]
        if isinstance(annual_dividend_ratios, float):
            yearly_dividend = float(annual_dividend_ratios)
        elif year in annual_dividend_ratios:
            yearly_dividend = annual_dividend_ratios[year]
        
        leverage_dividend_multiplier = self._known_index_data[self.KNOWN_FILE_NAMES[self._file_name]]["leverage_data"][leverage]["annual_expense_ratio"]
        return yearly_dividend * leverage_dividend_multiplier

    def get_annual_cost(self, year: int, leverage: Union[int, float]) -> float:
        if not CHARGE_ETF_EXPENSES:
            return 0.0

        leverage = float(leverage)
        if self._file_name not in self.KNOWN_FILE_NAMES or leverage not in {1.0, 2.0, 3.0}:
            return UNLEVERAGED_ETF_EXPENSE_RATIO if leverage == 1.0 else LEVERAGED_ETF_EXPENSE_RATIO
        
        return self._known_index_data[self.KNOWN_FILE_NAMES[self._file_name]]["leverage_data"][leverage]["annual_expense_ratio"]
        

dividend_cost_data = KnownIndexMetaData()

if __name__ == "__main__":
    index_meta_data = KnownIndexMetaData()
    print(index_meta_data._known_index_data)
