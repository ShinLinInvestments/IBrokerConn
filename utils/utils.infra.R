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

# Infra functions
x.p <- function(...) paste(..., sep='')

x.isYmd <- function(d) grepl('^[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9]$', as.character(d))

x.checkCond <- function(cond, err.message){
    if(all(cond)) return()
    flog.fatal(err.message)
    stop(err.message)
}

