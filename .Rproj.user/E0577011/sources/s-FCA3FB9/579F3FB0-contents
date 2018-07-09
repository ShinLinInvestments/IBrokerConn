library(data.table)
library(IBrokers)
IBrokersRef()

tws = twsConnect(clientId = 1, port = 7496)
acct = reqAccountUpdates(tws)
twsPortfolioValue(acct)

seco = twsFuture('YM', exch='ECBOT', expiry='201806')
pv0 = reqHistoricalData(tws, seco, barSize = '1 min', whatToShow = 'BID_ASK', duration = "1 D")
pv1 = data.table(datetime = index(pv0), pv0)
colnames(pv1) = c('datetime','Open','High','Low','Close','Vlm','wap','hasGaps','Count')
