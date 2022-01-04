Leveraged ETF simulator

# BACKGROUND:
Much misinformation surrounds holding leveraged ETFs long term. This simulation attempts to use real data to simulate ETF outcomes at different leverages compared with the underlying index.

It is known that volatility of a security can result in decay. While this may be true, my hypothesis is that the affect of the decay is frequently overplayed and investors shy away from an opportunity that could generate significant returns, returns that I suspect would far outpace the rate of decay.

While decay may exist in times of volatility where the security price remains constant, risk can be mitigated by investing in major indexes. Major U.S. indexes have historically gone up over their lifetime, such as the DJIA which has gone up over the past 100 years.

# HYPOTHESIS: 
My hypothesis is that a leverage of 1.9x, contrary to conventional investment wisdom, will result in much higher gains when invested in ETFs that accurately track (>.99) a major U.S. index.

# ASSUMPTIONS AND LIMITATIONS:
The following assumptions are made:
1. The leveraged ETF is held over a long period of time, that is, more than 2 years, but no more than 20 years. This is a study of holding leveraged ETFs long term, so they should be held long term. The amount of time the ETF is held should be randomized since investors frequently struggle to time an exit perfectly.*
2. It is assumed that investors cannot predict the future of an index's price. Therefore, entries into the market should be randomly selected.*
3. Dividends are not reinvested. This makes certain calculations difficult. Generally speaking though, leveraged ETFs do not offer as good of a dividend as a normal ETF. Eg compare DIA's 1.6% dividend to UDOW's .2% dividend.
4. There are no adjustments for inflation because the comparison is not against cash, but rather is against an index.
5. Taxes are ignored. Various ETFs are structured differently, resulting in different tax repercussions for the investor. Note that taxes can be due as frequently as a quarterly basis depending on the structure of the ETF, and taxes rates can vary (long term capital gains taxes, corporate taxes, and individual taxes).
6. Yearly management fees can be included in the calculation in the common.py file. A suggested 1% management fee would match most leveraged ETFs that track major U.S. indexes (eg UDOW, TQQQ, ... all charge .95%). If the leverage of the investment is 1.0, the leveraged ETF management fee in common.py will not apply.

*I am aware that different expertise, knowledge, metrics, and other factors can increase (or decrease) the odds of a well timed entry or exit, but because the average investor's entries and exits are quite random in relation to the short term (and sometimes even long term) outcome of the security, a random entry and exit seem to simulate actual investor behaviour the best.


# Experiment execution:
The experiment will go as follows:
- 1000 experiments will be ran with random entry and random exit points, with the exit point being between 2 years and 20 years of the entry point.
- The annualized rate of return will be recorded for that period on both a leveraged ETF and a normal ETF.
- The results will show the average annualized return of those 1000 experiments, worst return, and best return, average total return, percentage of time a leverage outperforms the index, along with other data.

The formula for calculating an annualized return based off a given period of time is:
annualized rate of return (%) = [[((price of security at entry)/(price of security at exit)) ^ (1 / number of years security is held)] - 1] * 100


# OUTCOME:
- Based on the indexes for the Dow Jones (1900 to 2021), NASDAQ-100 (1985 - 2021), and S&P500 (1900 to 2021), a leverage of 1.0 does not yield the highest annualized rate over the 1000 random long term entries and exits.
- While the exact optimal leverage for each varies, a leverage of 2.7 yields the optimal annualized average rate of return for all 3 indexes.
- A lower leverage (1.5-2.2) frequently outperforms the index at a much higher frequency, though the annualized rate of return is lower. Therefore, you could significantly reduce the chances of the normal index outperforming your investment by investing at a lower leverage if that is the concern.
- A leverage of 3.8-3.9 generates the largest average returns overall.
- It makes sense that 2.7 is the optimal leverage for maximum annualized rate of return. This nicely balances both the high risk/high payoff/high loss of the large average returns of 3.8 leverage, and the safe odds of outperforming the 1.0 index at a 1.5-2.2 leverage.


# DISCLAIMER:
**I am not offering investment advice. I am obviously not responsible for your investment outcomes. I am simulating these purely out of curiosity. Investing in leveraged ETFs, ETFs, or other securities, can result in loss of money (sometimes all of it) and debt.**
