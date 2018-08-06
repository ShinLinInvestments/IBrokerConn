library(IBrokers)
IBrokersRef()

tws = twsConnect(clientId = 1, port = 7496)
acct = reqAccountUpdates(tws)
twsPortfolioValue(acct)

seco = twsFuture('YM', exch='ECBOT', expiry='201809')
seco = twsFuture('NQ', exch='GLOBEX', expiry='201809')
pv0 = reqHistoricalData(tws, seco, barSize = '1 min', whatToShow = 'TRADES', useRTH = "0", duration = "1 M")
pv1 = data.table(datetime = index(pv0), pv0)
colnames(pv1) = c('datetime','Open','High','Low','Close','Vlm','wap','hasGaps','Count')

twsDisconnect(tws)

