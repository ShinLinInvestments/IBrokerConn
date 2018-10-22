import time
import xutils
import pandas as pd

app = xutils.IBApiMaster("127.0.0.1", 7496, 1)

secs = [('YM','ECBOT'), ('ES','GLOBEX'), ('NQ','GLOBEX')]

res = []
for si in secs:
    contractIB = xutils.ibapi.contract.Contract()
    contractIB.secType = "CONTFUT"
    contractIB.symbol = si[0]
    contractIB.exchange = si[1]

    contractIB = app.resolveContractIB(contractIB, reqId = 43, maxWaitSecs = 40)

    currentYMDHMS = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
    #currentYMDHMS = "20181012 15:00:00 America/New_York"
    historic_data = app.getHistoricalData(reqId = 51, contractIB = contractIB, maxWaitSecs = 200, endDateTime = currentYMDHMS,
                                      durationStr = '1 W', barSizeSetting = '30 secs', whatToShow = 'TRADES', useRTH = 0,
                                      formatDate = 1, keepUpToDate = False)
    historic_data['datetime'] = historic_data['datetime'].apply(lambda x : x.strftime("%Y%m%d.%H%M%S"))
    historic_data.insert(0, 'ticker', si[0])
    print(historic_data)
    res.append(historic_data)
res = pd.concat(res)
print(res)
#xutils.write_csv(historic_data, '/Volumes/Xingsiz500G/workspace/data/emini/ohlcv/ohlcv.', 'datetime')

app.disconnect()
