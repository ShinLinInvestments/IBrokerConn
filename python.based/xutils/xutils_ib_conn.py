import ibapi.client
import ibapi.wrapper
import threading
import queue
import pandas as pd
from xutils.xutils_environ import *

_utils_ib_isFinished = object()

class FinishableQueue(object):
    def __init__(self, queueToFinish):
        self._queue, self._status, self._timedOut = queueToFinish, None, object()

    def get(self, timeout):
        queueContents = []
        while not (self._status is self._timedOut or self._status is _utils_ib_isFinished):
            try:
                current_element = self._queue.get(timeout = timeout)
                if current_element is _utils_ib_isFinished:
                    self._status = _utils_ib_isFinished
                else:
                    queueContents.append(current_element)
            except queue.Empty:
                self._status = self._timedOut
        return queueContents

    def timed_out(self):
        return self._status is self._timedOut

class IBApiWrapper(ibapi.wrapper.EWrapper):
    # The wrapper deals with the action coming back from the IB gateway or TWS instance
    def __init__(self):
        self._contractDetailsDict, self._historicDataDict = {}, {}
        self.initError()

    # error handling code
    def initError(self):
        self._errorQueue = queue.Queue()

    def getError(self, timeout = 5):
        if self.isError():
            try:
                return self._errorQueue.get(timeout = timeout)
            except queue.Empty:
                return None
        return None

    def isError(self):
        return not self._errorQueue.empty()

    def error(self, id, errorCode, errorString):  # Overriding
        self._errorQueue.put("IBApiWrapper|errorID:%d|errorCode:%d|%s" % (id, errorCode, errorString))

    def ContractDetailsInit(self, reqId):
        contractDetailsQueue = self._contractDetailsDict[reqId] = queue.Queue()
        return contractDetailsQueue

    def contractDetails(self, reqId, contractDetails):  # Overriding
        if reqId not in self._contractDetailsDict: self.ContractDetailsInit(reqId)
        self._contractDetailsDict[reqId].put(contractDetails)

    def contractDetailsEnd(self, reqId):  # Overriding
        if reqId not in self._contractDetailsDict: self.ContractDetailsInit(reqId)
        self._contractDetailsDict[reqId].put(_utils_ib_isFinished)

    # Historic Data
    def historicalDataInit(self, reqId):
        historic_data_queue = self._historicDataDict[reqId] = queue.Queue()
        return historic_data_queue

    def historicalData(self, reqId, bar):  # Overriding
        barDataTuple = (pd.Timestamp(bar.date), bar.open, bar.high, bar.low, bar.close, bar.volume, bar.barCount, bar.average)
        if reqId not in self._historicDataDict: self.historicalDataInit(reqId)
        self._historicDataDict[reqId].put(barDataTuple)

    def historicalDataEnd(self, reqId, start: str, end: str):  # Overriding
        if reqId not in self._historicDataDict: self.historicalDataInit(reqId)
        self._historicDataDict[reqId].put(_utils_ib_isFinished)

class IBApiClient(ibapi.client.EClient):
    def __init__(self, wrapper):
        ibapi.client.EClient.__init__(self, wrapper)

    def resolveContractIB(self, contractIB, reqId, maxWaitSecs = 20):
        xlog.info("ContractDetails Req = " + str(reqId) + ": " + str(contractIB))
        contractDetailsQueue = FinishableQueue(self.ContractDetailsInit(reqId))
        self.reqContractDetails(reqId, contractIB)
        contractDetailsResponseList = contractDetailsQueue.get(timeout = maxWaitSecs)
        while self.wrapper.isError():
            xlog.warn(self.getError())
        if contractDetailsQueue.timed_out():
            xlog.warn("ContractDetails Req = " + str(reqId) + "expired after" + maxWaitSecs + "secs")
        if len(contractDetailsResponseList) == 0:
            xlog.warn("Failed to get additional contract details: returning unresolved contract")
            return contractIB
        if len(contractDetailsResponseList) > 1:
            xlog.warn("got multiple contracts using first one")
        return contractDetailsResponseList[0].contract

    def getHistoricalData(self, reqId:int, maxWaitSecs:int, contractIB:ibapi.contract.Contract, endDateTime:str, durationStr:str,
                               barSizeSetting:str, whatToShow:str, useRTH:int, formatDate:int, keepUpToDate:bool, chartOptions = []):
        ## Make a place to store the data we're going to return
        historicalDataQueue = FinishableQueue(self.historicalDataInit(reqId))

        # Request some historical data. Native method in EClient
        self.reqHistoricalData(reqId = reqId, contract = contractIB, endDateTime = endDateTime, durationStr = durationStr,
                               barSizeSetting = barSizeSetting, whatToShow = whatToShow, useRTH = useRTH, formatDate = formatDate,
                               keepUpToDate = keepUpToDate, chartOptions = chartOptions)
        historic_data = historicalDataQueue.get(timeout = maxWaitSecs)
        while self.wrapper.isError():
            xlog.warn(self.getError())
        if historicalDataQueue.timed_out():
            xlog.warn("HistoricalData Req" + reqId + "expired after" + maxWaitSecs + "secs")
        self.cancelHistoricalData(reqId)
        return pd.DataFrame(historic_data, columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'count', 'wap'])

class IBApiMaster(IBApiWrapper, IBApiClient):
    def __init__(self, ipaddress, portid, clientid):
        IBApiWrapper.__init__(self)
        IBApiClient.__init__(self, wrapper = self)
        self.connect(ipaddress, portid, clientid)
        thread = threading.Thread(target = self.run)
        thread.start()
        setattr(self, "_thread", thread)
        self.initError()
