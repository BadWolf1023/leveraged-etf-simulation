"""
/* Copyright (C) William Lyles - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by William Lyles <willglyles@gmail.com>, January 4th, 2022
 */
 """

from typing import List
from dateutil.parser import parse


def fix_dollars(amount:str) -> float:
    fixed_amount = amount.replace("$", "").replace(" ", "").replace(",", "")
    return round(float(fixed_amount), 2)

class DailyAssetData(object):

    def __init__(self, data:List[str], previous_day=None):
        self.date = parse(data[0]).date()
        self.open = fix_dollars(data[1])
        self.high = fix_dollars(data[2])
        self.low = fix_dollars(data[3])
        self.close = fix_dollars(data[4])
        self.volume = int(data[5]) if len(data) >= 6 else None
        self.dollar_change = 0.0
        self.ratio_change = 0.0
        if previous_day is not None:
            self.dollar_change = round(self.close - previous_day.close, 2)
            self.ratio_change = self.dollar_change / previous_day.close

    def get_previous_day_close(self):
        return round(self.close - self.dollar_change, 2)

    def __str__(self):
        return f"""Date: {self.date}
        Open:   ${self.open}
        High:   ${self.high}
        Low:    ${self.low}
        Close:  ${self.close}
        Volume: {self.volume}
        Change: ${self.dollar_change}
        Ratio:  {self.ratio_change}"""

    def __repr__(self):
        return str(self)
