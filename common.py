"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */
 """
file_names = ["dji_d.csv", "spx_d.csv", "ndx_d.csv"]
OUTPUT_FILE_NAME = "results.txt"

DAYS_PER_YEAR = 365.2422
STARTING_INVESTMENT_AMOUNT = 10000

NUMBER_OF_INVESTMENTS = 1000
MIN_INVESTMENT_YEARS = 2
MAX_INVESTMENT_YEARS = 20

MINIMUM_START_YEAR = None
MAXIMUM_END_YEAR = None
PRINT_EXTRA_STATS_ON_BEST_WORST = True
PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD = False
EXTRA_STAT_CAGR_THRESHOLD = .01  # This threshold is used for additional display stats when investment's CAGR is below or above this threshold - not used if PRINT_EXTRA_STATS_SPECIFIC_CAGR_THRESHOLD is False

PRINT_EXTRA_RETURN_THRESHOLD_STATS = True

PRINT_PROGRESS = True

DECREASE_LEVERAGE_AT_YEAR_END = True
YEAR_END_DECREASE = .01 #1%

USE_REALISTIC_SPLIT_LEVERAGE = True


def reversed_enumerate(collection: list):
    for i in range(len(collection)-1, -1, -1):
        yield i, collection[i]