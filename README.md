# Phytoplankton Indicator (Phase 2)

Technical documentation & reporting website for the Puget Sound Partnership Phytoplankton Indicator (Phase 2) project.

## Getting Started

### Setup

1. Install Quarto by following the [installation instructions](https://quarto.org/docs/getting-started/installation.html)
2. Install Python version 3.12 by following the [installation instructions](https://www.python.org/downloads/release/python-312/)
3. Install R version 4.4 by following the [installation instructions](https://cran.r-project.org/)
4. Clone the repository: `git clone https://github.com/GSIEnvironmental/Phytoplankton_Indicator_Phase2.git`
5. Move into the cloned repository: `cd Phytoplankton_Indicator_Phase2`
6. Create a Python virtual environment and activate it
   1. **Windows**: `python -m venv .venv; .\.venv\Scripts\activate`
   2. **Linux/MacOS**: `python -m venv .venv && source ./.venv/bin/activate`

   The Python virtual environment needs to be activated when rendering or previewing the site. This is because Quarto uses Python kernels to run code chunks embedded within the `.qmd` documents.
7. Install the Python requirements: `python -m pip install -r requirements.txt`
8. Setup `renv` for R dependencies: `Rscript -e 'renv::restore()'`

   > [!NOTE]
   > [renv](https://rstudio.github.io/renv/articles/renv.html) is an R package that creates a project-specific library to manage dependencies. The [`renv.lock`](./renv.lock) file contains a snapshot of the R packages used in this project. Running `renv::restore()` will install the necessary R packages in the project library.

9. (*optional*) Install `pre-commit` hooks: `python -m pre_commit install --install-hooks`

   > [!NOTE]
   > [Pre-commit](https://pre-commit.com/) hooks are composed of linters and formatters specifically selected for this project. Pre-commit will help keep our code files clean and make sure we are following best practices before committing changes. The pre-commit package is included in our Python [requirements](./requirements.txt). Hooks will run on the current commit snapshot when executing a `git commit`.

### Contributing

The following steps assume you have already completed all [setup](#setup) procedures.

> [!IMPORTANT]
> You do not need to render this project prior to committing changes to GitHub. The [GitHub Actions workflow](./.github/workflows/build-and-deploy.yaml) will automatically render the site when changes are pushed to the repository.

1. Pull the latest changes from GitHub:
   1. Checkout the main branch `git checkout main`
   2. Pull changes from the remote (GitHub) repository:  `git pull origin main`
   3. Create a new branch to make changes: `git checkout -b <branch-name>`
2. Activate the Python virtual environment:
   1. **Windows**: `.\.venv\Scripts\activate`
   2. **Linux/MacOS**: `source ./.venv/bin/activate`
3. Start the preview server to see changes in real-time: `quarto preview`
4. Make changes to an existing `.qmd` file, or create a new one. When creating new files and folders, follow [Kebab case](https://en.wikipedia.org/wiki/Letter_case#Kebab_case)
   1. When creating new `.qmd` files, you may need to restart the preview server for Quarto to recognize them: `CTRL+C` to stop the server, then `quarto preview` to restart.
5. Update [`_quarto.yml`](_quarto.yml) if changes to the repository structure are made.
6. If using `pre-commit`, now is a good time to check files for issues: `python -m pre_commit run --all-files`.
7. Once finished, render the site (this may take a couple minutes): `quarto render`

   > [!TIP]
   > Target specific sections or pages to render instead of the entire site such as `quarto render docs/data-management` or `quarto render docs/data-management/index.qmd`.

8. Stage your changes with git: `git add <files>`
   1. To stage all modified files: `git add --all`
9. Narrate and commit changes: `git commit -m "YOUR COMMIT MESSAGE"`
10. If you've installed `pre-commit`, it may halt your commit and prompt you to fix any linting errors. Make the changes, re-render the site, stage changes, and try again.
11. Push changes to the remote repository (GitHub): `git push origin <branch-name>`
12. Delete the branch and start over with step 1: `git checkout main && git branch -D <branch-name>`

#### Adding Python and R Packages

If new Python packages are installed, update the requirements file: `pip freeze > requirements.txt`

If new R packages are installed, update the lockfile: `Rscript -e "renv::snapshot()"`

## Quarto Extensions

The following Quarto [extensions](./_extensions/) are used in this project:

- [quarto-live](https://github.com/r-wasm/quarto-live)
- [bsicons](https://github.com/shafayetShafee/bsicons)
- [diagram](https://github.com/pandoc-ext/diagram)
- [material-icons](https://github.com/shafayetShafee/material-icons)
- [black-formatter](https://github.com/shafayetShafee/black-formatter)
- [downloadthis](https://github.com/shafayetShafee/downloadthis)
- [add-code-files](https://github.com/shafayetShafee/add-code-files)
- [code-fullscreen](https://github.com/shafayetShafee/code-fullscreen)
