source('utils/utils.R')

#IBrokersRef()

tws.conn = twsConnect(clientId = 1, port = 7496)
acct = reqAccountUpdates(tws.conn)
twsPortfolioValue(acct)

tws.future.ym = twsFuture('YM', exch='ECBOT', expiry='201809')
tws.future.nq = twsFuture('NQ', exch='GLOBEX', expiry='201809')

ym.data = x.ib.getHistoricalData(tws.conn, tws.future.ym, barSize = '30 secs', whatToShow = 'TRADES', useRTH = "0", duration = "1 M")
nq.data = x.ib.getHistoricalData(tws.conn, tws.future.nq, barSize = '30 secs', whatToShow = 'TRADES', useRTH = "0", duration = "1 M")



twsDisconnect(tws.conn)

