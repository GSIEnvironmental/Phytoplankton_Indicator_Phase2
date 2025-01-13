source("renv/activate.R")

## Set Environmental Variables on initialization of R session
local({
  set_env <- \(fp) if(file.exists(fp)) readRenviron(fp)
  set_env("_environment")
  set_env("_environment.local")
})
