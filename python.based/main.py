from utils.utils_ib import *

app = IBApiMaster("127.0.0.1", 7496, 1)

contractIB = ibapi.contract.Contract()
contractIB.secType = "FUT"
contractIB.lastTradeDateOrContractMonth = "201809"
contractIB.symbol = "NQ"
contractIB.exchange = "GLOBEX"

contractIB = app.resolveContractIB(contractIB)
print(contractIB)

historic_data = app.get_IB_historical_data(contractIB)

print(historic_data)

app.disconnect()
