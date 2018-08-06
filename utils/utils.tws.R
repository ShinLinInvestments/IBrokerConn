library(IBrokers)

x.ib.getHistoricalData <- function(tws.conn, tws.contract, ...){
    pv0 = reqHistoricalData(tws.conn, tws.contract, ...)
    all.datetimes = index(pv0)
    pv1 = data.table(date = format(all.datetimes, '%Y%m%d'), intv = format(all.datetimes, '%H%M%S'), pv0)
    colnames(pv1) = tolower(gsub('([a-z])([A-Z])', '\\1.\\2', gsub('.*\\.', '', colnames(pv1))))
    pv1
}

