"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */
 """

DAYS_PER_YEAR = 365.2422
STARTING_INVESTMENT_AMOUNT = 10000

DECREASE_LEVERAGE_AT_YEAR_END = True
YEAR_END_DECREASE = .01 #1%


def reversed_enumerate(collection: list):
    for i in range(len(collection)-1, -1, -1):
        yield i, collection[i]