import ibapi.client
import ibapi.wrapper
import threading
import queue
import datetime

DEFAULT_HISTORIC_DATA_ID = 50
DEFAULT_GET_CONTRACT_ID = 43

## marker for when queue is finished
FINISHED = object()
STARTED = object()
TIME_OUT = object()

class finishableQueue(object):
    def __init__(self, queue_to_finish):
        self._queue = queue_to_finish
        self.status = STARTED

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
                    self.status = FINISHED
                else:
                    contents_of_queue.append(current_element)
                    ## keep going and try and get more data

            except queue.Empty:
                ## If we hit a time out it's most probable we're not getting a finished element any time soon
                ## give up and return what we have
                finished = True
                self.status = TIME_OUT
        return (contents_of_queue)

    def timed_out(self):
        return self.status is TIME_OUT

class ibApiWrapper(ibapi.wrapper.EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance
    We override methods in EWrapper that will get called when this action happens, like currentTime
    Extra methods are added as we need to store the results in this object
    """

    def __init__(self):
        self._ibContractDetails = {}
        self._historicDataDict = {}
        self.initError()

    ## error handling code
    def initError(self):
        self._errorQueue = queue.Queue()

    def getError(self, timeout = 5):
        if self.isError():
            try:
                return (self._errorQueue.get(timeout = timeout))
            except queue.Empty:
                return None
        return None

    def isError(self):
        return not self._errorQueue.empty()

    def error(self, id, errorCode, errorString):  # Overriding
        self._errorQueue.put("IB errorID:%d errorCode:%d %s" % (id, errorCode, errorString))

    def initContractDetails(self, reqId):
        contractDetailsQueue = self._ibContractDetails[reqId] = queue.Queue()
        return contractDetailsQueue

    def contractDetails(self, reqId, contractDetails):  # Overriding
        if reqId not in self._ibContractDetails:
            self.initContractDetails(reqId)
        self._ibContractDetails[reqId].put(contractDetails)

    def contractDetailsEnd(self, reqId):  # Overriding
        if reqId not in self._ibContractDetails:
            self.initContractDetails(reqId)
        self._ibContractDetails[reqId].put(FINISHED)

    ## Historic data code
    def initHistoricData(self, tickerid):
        historic_data_queue = self._historicDataDict[tickerid] = queue.Queue()

        return (historic_data_queue)

    def historicalData(self, tickerid, bar):
        bardata = (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)
        historic_data_dict = self._historicDataDict

        ## Add on to the current data
        if tickerid not in historic_data_dict.keys():
            self.initHistoricData(tickerid)

        historic_data_dict[tickerid].put(bardata)

    def historicalDataEnd(self, tickerid, start: str, end: str):
        ## overriden method

        if tickerid not in self._historicDataDict.keys():
            self.initHistoricData(tickerid)

        self._historicDataDict[tickerid].put(FINISHED)

class TestClient(ibapi.client.EClient):
    def __init__(self, wrapper):
        ibapi.client.EClient.__init__(self, wrapper)

    def resolve_ib_contract(self, ibcontract, reqId = DEFAULT_GET_CONTRACT_ID):

        """
        From a partially formed contract, returns a fully fledged version
        :returns fully resolved IB contract
        """

        ## Make a place to store the data we're going to return
        contractDetailsQueue = finishableQueue(self.initContractDetails(reqId))

        print("Getting full contract details from the server... ")

        self.reqContractDetails(reqId, ibcontract)

        ## Run until we get a valid contract(s) or get bored waiting
        MAX_WAIT_SECONDS = 100
        new_contract_details = contractDetailsQueue.get(timeout = MAX_WAIT_SECONDS)

        while self.wrapper.isError():
            print(self.getError())

        if contractDetailsQueue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")

        if len(new_contract_details) == 0:
            print("Failed to get additional contract details: returning unresolved contract")
            return (ibcontract)

        if len(new_contract_details) > 1:
            print("got multiple contracts using first one")

        new_contract_details = new_contract_details[0]

        resolved_ibcontract = new_contract_details.contract

        return (resolved_ibcontract)

    def get_IB_historical_data(self, ibcontract, durationStr = "1 Y", barSizeSetting = "1 day",
                               tickerid = DEFAULT_HISTORIC_DATA_ID):

        """
        Returns historical prices for a contract, up to today
        ibcontract is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """

        ## Make a place to store the data we're going to return
        historic_data_queue = finishableQueue(self.initHistoricData(tickerid))

        # Request some historical data. Native method in EClient
        self.reqHistoricalData(
            tickerid,  # tickerId,
            ibcontract,  # contract,
            datetime.datetime.today().strftime("%Y%m%d %H:%M:%S %Z"),  # endDateTime,
            durationStr,  # durationStr,
            barSizeSetting,  # barSizeSetting,
            "TRADES",  # whatToShow,
            1,  # useRTH,
            1,  # formatDate
            False,  # KeepUpToDate <<==== added for api 9.73.2
            []  ## chartoptions not used
        )

        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 100
        print("Getting historical data from the server... could take %d seconds to complete " % MAX_WAIT_SECONDS)

        historic_data = historic_data_queue.get(timeout = MAX_WAIT_SECONDS)

        while self.wrapper.isError():
            print(self.getError())

        if historic_data_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")

        self.cancelHistoricalData(tickerid)

        return (historic_data)

class ibApiMaster(ibApiWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        ibApiWrapper.__init__(self)
        TestClient.__init__(self, wrapper = self)
        self.connect(ipaddress, portid, clientid)
        thread = threading.Thread(target = self.run)
        thread.start()
        setattr(self, "_thread", thread)
        self.initError()

# if __name__ == '__main__':

app = ibApiMaster("127.0.0.1", 7496, 1)

ibcontract = ibapi.contract.Contract()
ibcontract.secType = "FUT"
ibcontract.lastTradeDateOrContractMonth = "201809"
ibcontract.symbol = "NQ"
ibcontract.exchange = "GLOBEX"

resolved_ibcontract = app.resolve_ib_contract(ibcontract)
print(resolved_ibcontract)

historic_data = app.get_IB_historical_data(resolved_ibcontract)

print(historic_data)

app.disconnect()
