library(IBrokers)

x.ib.getHistoricalData <- function(tws.conn, tws.contracts, start.date, end.date = format(Sys.Date(), '%Y%m%d'), ...){
    x.checkCond(x.isYmd(start.date), paste('start.date =', start.date, 'not valid'))
    x.checkCond(x.isYmd(end.date), paste('end.date =', end.date, 'not valid'))
    if(tolower(class(tws.contracts)) != 'twscontract'){
        return(rbindlist(lapply(tws.contracts, function(tws.contract) x.ib.getHistoricalData(tws.conn, tws.contract, start.date, end.date, ...)), use.names = TRUE, fill = TRUE))
    }
    contract.specs.df = t(data.frame(value=unlist(tws.contracts)[which(!unlist(tws.contracts) %in% c('', '0'))]))
    contract.specs.print = paste(colnames(contract.specs.df), '=', as.character(contract.specs.df), collapse = ', ')
    cur.end.datetime = paste(end.date, '23:59:59')
    cur.end.date = end.date
    res = c()
    while(cur.end.date >= start.date){
        pv0 = reqHistoricalData(tws.conn, tws.contracts, endDateTime = cur.end.datetime, duration = "1 D", ...)
        pv1 = data.table(pv0)
        all.datetimes = index(pv0)
        pv1 = data.table(date = format(all.datetimes, '%Y%m%d'), intv = format(all.datetimes, '%H:%M:%S'), contract.specs.df[rep(1,nrow(pv1)),], pv1)
        colnames(pv1) = tolower(gsub('([a-z])([A-Z])', '\\1.\\2', gsub('.*\\.', '', colnames(pv1))))
        pv1 = pv1[order(date, intv)]
        res = rbind(pv1, res)
        next.start.datetime = pv1[1, paste(date, intv)]
        flog.info(paste('Retrieved', contract.specs.print, 'from', next.start.datetime, 'to', pv1[nrow(pv1), paste(date, intv)]))
        cur.end.datetime = next.start.datetime
        cur.end.date = pv1[1, date]
    }
    res
}

