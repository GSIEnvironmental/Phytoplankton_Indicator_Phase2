source("renv/activate.R")

## Set Environmental Variables on initialization of R session
local({
  set_env <- \(fp) if(file.exists(fp)) readRenviron(fp)
  set_env("_environment")
  set_env("_environment.local")
  # reticulate seems to be required by the knitr engine to use python and r chunks in the same .qmd file
  reticulate::use_virtualenv('./.venv', required=TRUE) 
})
