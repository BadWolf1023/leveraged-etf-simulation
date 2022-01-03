# Leveraged ETF Simulation
 
 """
Leveraged ETF simulator

Much misinformation surrounds holding leveraged ETFs long term. This simulation attempts to use real data to simulate a 2x leveraged ETF outcome and a 3x leveraged ETF outcome compared with the underlying index.

It is known that volatility of a security can result in decay. While this may be true, my hypothesis is that the affect of the decay is frequently overplayed and investors shy away from an opportunity
could generate significant returns, and that the returns frequently far outpace the rate of decay.

While decay may exist in times of volatility where the security price remains constant, risk can be mitigated by investing in major indexes. Major U.S. indexes have historically gone up over their lifetime, such as the DJIA which has gone up over the past 100 years.

Therefore, while the increased exposure 

My hypothesis is that a leverage of 1.9x, contrary to conventional investment wisdom, will result in much higher gains when invested in ETFs that accurately track (>.99) a major U.S. index.

The following assumptions are made:
1. The leveraged ETF is held over a long period of time, that is, more than 2 years, but no more than 20 years. This is a study of holding leveraged ETFs long term, so they should be held long term. The amount of time the ETF is held should be randomized since investors frequently struggle to time an exit perfectly.*
2. It is assumed that investors cannot predict the future of an index's price. Therefore, entries into the market should be randomly selected.*
3. Dividends are not reinvested. This makes certain calculations difficult. Generally speaking though, leveraged ETFs do not offer as good of a dividend as a normal ETF. Eg compare DIA's 1.6% dividend to UDOW's .2% dividend.
4. The management fee is waived. This makes certain calculations difficult as the management fee can fluctuate from year to year, even for normal ETFs. Generally speaking though, leveraged ETFs have a management fee of around 1%,
and normal ETFs can vary between free managament and .5% (higher for international ETFs).
5. There are no adjustments for inflation because the comparison is not against cash, but rather is against an index.
6. Taxes are ignored. Various ETFs are structured differently, result in different tax reprucussions for the investor. Note that taxes can be due as frequently as a quarterly basis depending on the structure of the ETF,
and taxes rates can vary (long term capital gains taxes, corporate taxes, and individual taxes).

*I am aware that different expertise, knowledge, metrics, and other factors can increase (or decrease) the odds of a well timed entry or exit, but because the average investor's entries and exits are quite random in relation to
the short term (and sometimes even long term) outcome of the security, a random entry and exit seem to simulate best actual investor behaviour.



The experiment will go as follows:
- 100 experiments will be ran with random entry and random exit points, with the exit point being between 2 years and 20 years of the entry point.
- The annualized rate of return will be recorded for that period on both a leveraged ETF and a normal ETF.
- The results will show the average annualized return of those 100 experiments, worst return, and best return.




The formula for calculating an annualized return based off a given period of time is:
annualized rate of return (%) = [[((price of security at entry)/(price of security at exit)) ^ (1 / number of years security is held)] - 1] * 100


OUTCOME: TBD

DISCLAIMER: I am not offering investment advice. I am obviously not responsible for your investment outcomes. I am simulating these purely out of curiosity. Investing in leveraged ETFs, ETFs, or other securities, can result in
"""
