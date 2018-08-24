library(data.table)
library(IBrokers)

x.info.append <- function(tws.contract, msuk){
    x.checkCond(tolower(class(tws.contract)) == 'twscontract', paste('input is not twsContract'))
    info.cur = read.csv('../info/sec.info.csv')
    info.new = data.table(msuk, t(data.frame(unlist(tws.future.es))))
    res = rbind(info.cur, info.new)
    write.csv(res, '../info/sec.info.csv', quote = FALSE, row.names = FALSE)
}