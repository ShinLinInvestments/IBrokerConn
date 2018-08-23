library(data.table)
library(parallel)
library(futile.logger)

# Time and Language setup
if(tolower(Sys.info()['sysname']) == 'darwin'){
    Sys.setlocale("LC_TIME", "en_US.UTF-8")
} else if(tolower(Sys.info()['sysname']) == 'windows'){
    Sys.setlocale("LC_TIME", "English")
}

# Logging
flog.layout(layout.format('~t|~l|~n|~f|~m'))
flog.threshold(DEBUG)

# General Infra
x.p <- function(...) paste(..., sep='')

x.checkCond <- function(cond, err.message){
    if(all(cond)) return()
    flog.fatal(err.message)
    stop(err.message)
}

# Datetime Infra
x.isYmd <- function(d) grepl('^[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9]$', as.character(d))
x.isHMS <- function(intv) grepl('^[0-2][0-9]:[0-5][0-9]:[0-5][0-9]$', as.character(intv))

x.ymdhms2POSIXct <- function(ymd, intv){
    x.checkCond(x.isYmd(ymd), paste('date =', ymd, 'not valid'))
    x.checkCond(x.isHMS(intv), paste('intv =', intv, 'not valid'))
    as.POSIXct(paste(ymd, intv), format = '%Y%m%d %H:%M:%S')
}