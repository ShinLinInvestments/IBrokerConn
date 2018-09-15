from utils.utils_ib import *
import time

app = IBApiMaster("127.0.0.1", 7496, 1)

contractIB = ibapi.contract.Contract()
contractIB.secType = "FUT"
contractIB.lastTradeDateOrContractMonth = "201809"
contractIB.symbol = "ES"
contractIB.exchange = "GLOBEX"

contractIB = app.resolveContractIB(contractIB)
print(contractIB)

currentYMDHMS = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
historic_data = app.getHistoricalData(reqId = 51, contractIB = contractIB, maxWaitSecs = 200, endDateTime = currentYMDHMS,
                                      durationStr = '1 W', barSizeSetting = '30 secs', whatToShow = 'TRADES', useRTH = 0,
                                      formatDate = 1, keepUpToDate = False)

print(historic_data)

app.disconnect()
