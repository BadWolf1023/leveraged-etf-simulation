DAYS_PER_YEAR = 365.2422
STARTING_INVESTMENT_AMOUNT = 10000

DECREASE_LEVERAGE_AT_YEAR_END = True
YEAR_END_DECREASE = .01 #1%

def reversed_enumerate(collection: list):
    for i in range(len(collection)-1, -1, -1):
        yield i, collection[i]