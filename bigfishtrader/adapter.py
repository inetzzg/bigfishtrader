# encoding: utf-8

from bigfishtrader.const import *
from bigfishtrader.models.data import *
from bigfishtrader.vt.vtConstant import *
from bigfishtrader.vt.vtGateway import VtOrderReq, VtSubscribeReq

MAP_VT_DIRECTION = {
    DIRECTION_NONE: DIRECTION.NONE.value,
    DIRECTION_LONG: DIRECTION.LONG.value,
    DIRECTION_SHORT: DIRECTION.SHORT.value,
    DIRECTION_UNKNOWN: DIRECTION.UNKNOWN.value,
    DIRECTION_NET: DIRECTION.UNKNOWN.value,
}

MAP_VT_DIRECTION_REVERSE = {
    DIRECTION.NONE.value: DIRECTION_NONE,
    DIRECTION.LONG.value: DIRECTION_LONG,
    DIRECTION.SHORT.value: DIRECTION_SHORT,
    DIRECTION.UNKNOWN.value: DIRECTION_UNKNOWN,
}

MAP_VT_OFFSET = {
    OFFSET_NONE: ACTION.NONE.value,
    OFFSET_OPEN: ACTION.OPEN.value,
    OFFSET_CLOSE: ACTION.CLOSE.value,
    OFFSET_UNKNOWN: ACTION.UNKNOWN.value,
}

MAP_VT_OFFSET_REVERSE = {
    ACTION.NONE.value: OFFSET_NONE,
    ACTION.OPEN.value: OFFSET_OPEN,
    ACTION.CLOSE.value: OFFSET_CLOSE,
    ACTION.UNKNOWN.value: OFFSET_UNKNOWN,
}

MAP_VT_STATUS = {
    STATUS_NOTTRADED: ORDERSTATUS.NOTTRADED.value,
    STATUS_PARTTRADED: ORDERSTATUS.PARTTRADED.value,
    STATUS_ALLTRADED: ORDERSTATUS.ALLTRADED.value,
    STATUS_CANCELLED: ORDERSTATUS.CANCELLED.value,
    STATUS_UNKNOWN: ORDERSTATUS.UNKNOWN.value,
}

MAP_VT_STATUS_REVERSE = {
    ORDERSTATUS.NOTTRADED.value: STATUS_NOTTRADED,
    ORDERSTATUS.PARTTRADED.value: STATUS_PARTTRADED,
    ORDERSTATUS.ALLTRADED.value: STATUS_ALLTRADED,
    ORDERSTATUS.CANCELLED.value: STATUS_CANCELLED,
    ORDERSTATUS.UNKNOWN.value: STATUS_UNKNOWN,
}

MAP_VT_PRICETYPE = {
    PRICETYPE_LIMITPRICE: ORDERTYPE.LIMIT.value,
    PRICETYPE_MARKETPRICE: ORDERTYPE.MARKET.value,
    PRICETYPE_FAK: ORDERTYPE.FAK.value,
    PRICETYPE_FOK: ORDERTYPE.FOK.value,
}

MAP_VT_PRICETYPE_REVERSE = {
    ORDERTYPE.MARKET.value: ORDERTYPE.MARKET,
    ORDERTYPE.LIMIT.value: ORDERTYPE.LIMIT,
    ORDERTYPE.FAK.value: ORDERTYPE.FAK,
    ORDERTYPE.FOK.value: ORDERTYPE.FOK,
}

# 合约类型映射
productClassMap = {}
productClassMap[PRODUCT_EQUITY] = 'STK'
productClassMap[PRODUCT_FUTURES] = 'FUT'
productClassMap[PRODUCT_OPTION] = 'OPT'
productClassMap[PRODUCT_FOREX] = 'CASH'
productClassMap[PRODUCT_INDEX] = 'IND'
productClassMapReverse = {v: k for k, v in productClassMap.items()}

# 期权类型映射
optionTypeMap = {}
optionTypeMap[OPTION_CALL] = 'CALL'
optionTypeMap[OPTION_PUT] = 'PUT'
optionTypeMapReverse = {v: k for k, v in optionTypeMap.items()}

# 货币类型映射
currencyMap = {}
currencyMap[CURRENCY_USD] = 'USD'
currencyMap[CURRENCY_CNY] = 'CNY'
currencyMap[CURRENCY_HKD] = 'HKD'
currencyMapReverse = {v: k for k, v in currencyMap.items()}

# 交易所类型映射
exchangeMap = {}
exchangeMap[EXCHANGE_SMART] = 'SMART'
exchangeMap[EXCHANGE_NYMEX] = 'NYMEX'
exchangeMap[EXCHANGE_GLOBEX] = 'GLOBEX'
exchangeMap[EXCHANGE_IDEALPRO] = 'IDEALPRO'
exchangeMap[EXCHANGE_HKEX] = 'HKEX'
exchangeMap[EXCHANGE_HKFE] = 'HKFE'
exchangeMapReverse = {v: k for k, v in exchangeMap.items()}


class VtAdapter(object):
    @classmethod
    def transform(cls, data):
        try:
            func = getattr(cls, "transform_" + data.__class__.__name__)
        except AttributeError:
            raise TypeError("VtAdapter don't support transformation of type: %s" % data.__class__)
        return func(data)

    @classmethod
    def transform_VtAccountData(cls, data):
        """

        Args:
            data(bigfishtrader.vt.vtGateway.VtAccountData):

        Returns:
            bigfishtrader.models.AccountData
        """
        account = AccountData()
        account.accountID = data.accountID
        account.gateway = data.gatewayName

        account.preBalance = data.preBalance
        account.balance = data.balance
        account.available = data.available
        account.commission = data.commission
        account.margin = data.margin
        account.closePnL = data.closeProfit
        account.positionPnL = data.positionProfit
        return account

    @classmethod
    def transform_VtTickData(cls, data):
        """

        Args:
            data(bigfishtrader.vt.vtGateway.VtTickData)

        Returns:
            bigfishtrader.models.TickData
        """
        tick = TickData()
        tick.symbol = data.symbol
        tick.exchange = data.exchange

        tick.lastPrice = data.lastPrice
        tick.lastVolume = data.lastVolume
        tick.volume = data.volume
        tick.openInterest = data.openInterest
        tick.time = data.time
        tick.date = data.date

        tick.openPrice = data.openPrice
        tick.highPrice = data.highPrice
        tick.lowPrice = data.lowPrice
        tick.preClose = data.preClosePrice

        tick.upperLimit = data.upperLimit
        tick.lowerLimit = data.lowerLimit

        tick.depth = 5
        tick.askPrice[0] = data.askPrice1
        tick.askPrice[1] = data.askPrice2
        tick.askPrice[2] = data.askPrice3
        tick.askPrice[3] = data.askPrice4
        tick.askPrice[4] = data.askPrice5
        tick.askVolume[0] = data.askVolume1
        tick.askVolume[1] = data.askVolume2
        tick.askVolume[2] = data.askVolume3
        tick.askVolume[3] = data.askVolume4
        tick.askVolume[4] = data.askVolume5
        tick.bidPrice[0] = data.bidPrice1
        tick.bidPrice[1] = data.bidPrice2
        tick.bidPrice[2] = data.bidPrice3
        tick.bidPrice[3] = data.bidPrice4
        tick.bidPrice[4] = data.bidPrice5
        tick.bidVolume[0] = data.bidVolume1
        tick.bidVolume[1] = data.bidVolume2
        tick.bidVolume[2] = data.bidVolume3
        tick.bidVolume[3] = data.bidVolume4
        tick.bidVolume[4] = data.bidVolume5
        return tick

    @classmethod
    def transform_VtPositionData(cls, data):
        """


        Args:
            data(bigfishtrader.vt.vtGateway.VtPositionData):

        Returns:
            bigfishtrader.models.PositionData
        """
        position = PositionData()
        position.symbol = data.symbol
        position.exchange = data.exchange
        position.side = MAP_VT_DIRECTION[data.direction]
        position.volume = data.position
        position.frozenVolume = data.frozen
        position.avgPrice = data.price
        return position

    @classmethod
    def transform_VtOrderData(cls, data):
        """

        Args:
            data(bigfishtrader.vt.vtGateway.VtOrderData):

        Returns:
            bigfishtrader.models.OrderStatusData
        """
        order_status = OrderStatusData()
        order_status.symbol = data.symbol
        order_status.exchange = data.exchange

        order_status.clOrdID = data.orderID
        order_status.secondaryClOrdID = data.frontID + "_" + data.sessionID
        order_status.side = MAP_VT_DIRECTION[data.direction]
        order_status.action = MAP_VT_OFFSET[data.offset]
        order_status.price = data.offset
        order_status.orderQty = data.totalVolume
        order_status.cumQty = data.tradedVolume
        order_status.leavesQty = data.totalVolume - data.tradedVolume
        order_status.ordStatus = MAP_VT_STATUS[data.status]
        order_status.orderTime = data.orderTime
        order_status.cancelTime = data.cancelTime
        order_status.gateway = data.gatewayName
        return order_status

    @classmethod
    def transform_VtErrorData(cls, data):
        """

        Args:
            data(bigfishtrader.vt.vtGateway.VtErrorData):

        Returns:
            bigfishtrader.models.ErrorData
        """
        error = ErrorData()
        error.errorID = data.errorID
        error.errorMsg = data.errorMsg
        error.errorTime = data.errorTime
        error.gateway = data.gatewayName
        return error

    @classmethod
    def transform_VtLogData(cls, data):
        """

        Args:
            data(bigfishtrader.vt.vtGateway.VtLogData):

        Returns:
            bigfishtrader.models.LogData
        """
        log = LogData()
        log.logTime = data.logTime
        log.logContent = data.logContent
        log.gateway = data.gatewayName
        return log

    @classmethod
    def transform_OrderReq(cls, data):
        """

        Args:
            data(bigfishtrader.models.OrderReq):

        Returns:
            bigfishtrader.vt.vtGateway.VtOrderReq
        """
        vt_order = VtOrderReq()
        vt_order.symbol = data.symbol
        vt_order.exchange = data.exchange
        vt_order.price = data.price
        vt_order.volume = data.orderQty
        vt_order.priceType = MAP_VT_PRICETYPE_REVERSE[data.ordType]
        vt_order.direction = MAP_VT_DIRECTION_REVERSE[data.side]
        vt_order.offset = MAP_VT_DIRECTION_REVERSE[data.action]
        return vt_order

    @classmethod
    def transform_ContractData(cls, data):
        """

        Args:
            data(bigfishtrader.models.data.ContractData):

        Returns:
            bigfishtrader.vt.vtGateway.VtSubscribeReq
        """
        sub_req = VtSubscribeReq()
        sub_req.symbol = data.longName
        sub_req.exchange = exchangeMapReverse[data.exchange]
        sub_req.productClass = productClassMapReverse[data.secType]
        sub_req.currency = data.currency
        sub_req.expiry = data.expiry
        sub_req.strikePrice = data.strike
        sub_req.optionType = data.right
        return sub_req
