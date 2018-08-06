library(IBrokers)

x.ib.getHistoricalData <- function(tws.conn, tws.contracts, ...){
    if(tolower(class(tws.contracts)) != 'twscontract'){
        return(rbindlist(lapply(tws.contracts, function(tws.contract) x.ib.getHistoricalData(tws.conn, tws.contract, ...)), use.names = TRUE, fill = TRUE))
    }
    contract.specs.df = t(data.frame(value=unlist(tws.contracts)[which(!unlist(tws.contracts) %in% c('', '0'))]))
    flog.info(paste('Retrieving', paste(colnames(contract.specs.df), '=', as.character(contract.specs.df), collapse = ', ')))
    pv0 = reqHistoricalData(tws.conn, tws.contracts, ...)
    pv1 = data.table(pv0)
    all.datetimes = index(pv0)
    pv1 = data.table(date = format(all.datetimes, '%Y%m%d'), intv = format(all.datetimes, '%H%M%S'), contract.specs.df[rep(1,nrow(pv1)),], pv1)
    colnames(pv1) = tolower(gsub('([a-z])([A-Z])', '\\1.\\2', gsub('.*\\.', '', colnames(pv1))))
    pv1
}

