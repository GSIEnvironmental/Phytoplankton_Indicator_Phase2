# Phytoplankton Indicator (Phase 2)

## Development

### Setup

- Install Python 3.12
- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment: `source .venv/bin/activate` (Linux) or `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- If new Python packages are installed, update the requirements file: `pip freeze > requirements.txt`
- Install R 4.4.2
- Restore the renv library: `Rscript -e "renv::restore()"`
- If new R packages are installed, update the lockfile: `Rscript -e "renv::snapshot()"`

## Extensions

- [quarto-live](https://github.com/r-wasm/quarto-live)
- [bsicons](https://github.com/shafayetShafee/bsicons)
- [diagram](https://github.com/pandoc-ext/diagram)
- [material-icons](https://github.com/shafayetShafee/material-icons)
- [black-formatter](https://github.com/shafayetShafee/black-formatter)
- [downloadthis](https://github.com/shafayetShafee/downloadthis)
- [add-code-files](https://github.com/shafayetShafee/add-code-files)
- [code-fullscreen](https://github.com/shafayetShafee/code-fullscreen)

```sh
quarto add --no-prompt r-wasm/quarto-live
quarto add --no-prompt shafayetShafee/bsicons
quarto add --no-prompt pandoc-ext/diagram
quarto add --no-prompt shafayetShafee/material-icons
quarto add --no-prompt shafayetShafee/black-formatter
quarto add --no-prompt shafayetShafee/downloadthis
quarto add --no-prompt shafayetShafee/add-code-files
quarto add --no-prompt shafayetShafee/code-fullscreen
```
