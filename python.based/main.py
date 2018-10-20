import time
import xutils
import datetime

app = xutils.IBApiMaster("127.0.0.1", 7496, 1)

contractIB = xutils.ibapi.contract.Contract()
contractIB.secType = "CONTFUT"
contractIB.symbol = "ES"
contractIB.exchange = "GLOBEX"

contractIB = app.resolveContractIB(contractIB, reqId = 43, maxWaitSecs = 40)
print(contractIB)

currentYMDHMS = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
#currentYMDHMS = "20181012 15:00:00 America/New_York"
historic_data = app.getHistoricalData(reqId = 51, contractIB = contractIB, maxWaitSecs = 200, endDateTime = currentYMDHMS,
                                      durationStr = '1 W', barSizeSetting = '30 secs', whatToShow = 'TRADES', useRTH = 0,
                                      formatDate = 1, keepUpToDate = False)

print(historic_data)

xutils.write_csv(historic_data, 'path', 'datetime')

app.disconnect()
