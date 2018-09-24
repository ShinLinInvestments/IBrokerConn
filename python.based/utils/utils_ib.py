import ibapi.client
import ibapi.wrapper
import threading
import queue
import pandas as pd
import re

FINISHED, TIME_OUT = object(), object()

class finishableQueue(object):
    def __init__(self, queue_to_finish):
        self._queue, self._status = queue_to_finish, None

    def get(self, timeout):
        """
        Returns a list of queue elements once timeout is finished, or a FINISHED flag is received in the queue
        :param timeout: how long to wait before giving up
        :return: list of queue elements
        """
        contents_of_queue = []
        finished = False
        while not finished:
            try:
                current_element = self._queue.get(timeout = timeout)
                if current_element is FINISHED:
                    finished = True
                    self._status = FINISHED
                else:
                    contents_of_queue.append(current_element)
                    ## keep going and try and get more data

            except queue.Empty:
                ## If we hit a time out it's most probable we're not getting a finished element any time soon
                ## give up and return what we have
                finished = True
                self._status = TIME_OUT
        return contents_of_queue

    def timed_out(self):
        return self._status is TIME_OUT

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
        self._contractDetailsDict[reqId].put(FINISHED)

    # Historic Data
    def historicalDataInit(self, reqId):
        historic_data_queue = self._historicDataDict[reqId] = queue.Queue()
        return historic_data_queue

    def historicalData(self, reqId, bar):  # Overriding
        dateintvTuple = tuple(re.split('[ ]+', bar.date))
        barDataTuple = dateintvTuple + (bar.open, bar.high, bar.low, bar.close, bar.volume, bar.barCount, bar.average)
        if reqId not in self._historicDataDict: self.historicalDataInit(reqId)
        self._historicDataDict[reqId].put(barDataTuple)

    def historicalDataEnd(self, reqId, start: str, end: str):  # Overriding
        if reqId not in self._historicDataDict: self.historicalDataInit(reqId)
        self._historicDataDict[reqId].put(FINISHED)

class IBApiClient(ibapi.client.EClient):
    def __init__(self, wrapper):
        ibapi.client.EClient.__init__(self, wrapper)

    def resolveContractIB(self, contractIB, reqId, maxWaitSecs = 20):
        contractDetailsQueue = finishableQueue(self.ContractDetailsInit(reqId))
        self.reqContractDetails(reqId, contractIB)
        contractDetailsResponseList = contractDetailsQueue.get(timeout = maxWaitSecs)

        while self.wrapper.isError():
            print(self.getError())
        if contractDetailsQueue.timed_out():
            print("ContractDetails Req", reqId, "expired after", maxWaitSecs, "secs")
        if len(contractDetailsResponseList) == 0:
            print("Failed to get additional contract details: returning unresolved contract")
            return contractIB
        if len(contractDetailsResponseList) > 1:
            print("got multiple contracts using first one")
        return contractDetailsResponseList[0].contract

    def getHistoricalData(self, reqId:int, maxWaitSecs:int, contractIB:ibapi.contract.Contract, endDateTime:str, durationStr:str,
                               barSizeSetting:str, whatToShow:str, useRTH:int, formatDate:int, keepUpToDate:bool, chartOptions = []):

        """
        Returns historical prices for a contract, up to today
        contractIB is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """
        ## Make a place to store the data we're going to return
        historicalDataQueue = finishableQueue(self.historicalDataInit(reqId))

        # Request some historical data. Native method in EClient
        self.reqHistoricalData(reqId = reqId, contract = contractIB, endDateTime = endDateTime, durationStr = durationStr,
                               barSizeSetting = barSizeSetting, whatToShow = whatToShow, useRTH = useRTH, formatDate = formatDate,
                               keepUpToDate = keepUpToDate, chartOptions = chartOptions)
        historic_data = historicalDataQueue.get(timeout = maxWaitSecs)
        while self.wrapper.isError():
            print(self.getError())
        if historicalDataQueue.timed_out():
            print("HistoricalData Req", reqId, "expired after", maxWaitSecs, "secs")
        self.cancelHistoricalData(reqId)
        return pd.DataFrame(historic_data, columns = ['date', 'intv', 'open', 'high', 'low', 'close', 'volume', 'count', 'wap'])

class IBApiMaster(IBApiWrapper, IBApiClient):
    def __init__(self, ipaddress, portid, clientid):
        IBApiWrapper.__init__(self)
        IBApiClient.__init__(self, wrapper = self)
        self.connect(ipaddress, portid, clientid)
        thread = threading.Thread(target = self.run)
        thread.start()
        setattr(self, "_thread", thread)
        self.initError()
