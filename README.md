# Phytoplankton Indicator (Phase 2)

[![publish](https://github.com/GSIEnvironmental/Phytoplankton_Indicator_Phase2/actions/workflows/publish.yaml/badge.svg)](https://github.com/GSIEnvironmental/Phytoplankton_Indicator_Phase2/actions/workflows/publish.yaml)

Technical documentation & reporting for the Puget Sound Partnership Phytoplankton Indicator (Phase 2) project.

## Getting Started

### Setup

1. Install Quarto version >= 1.6 by following the [installation instructions](https://quarto.org/docs/getting-started/installation.html)
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
9. (*optional*) Install `pre-commit` hooks. [Pre-commit](https://pre-commit.com/) hooks are composed of linters and formatters specifically selected for this project. Pre-commit will help keep our code files clean and make sure we are following best practices before committing changes. The pre-commit package is included in our Python [requirements](./requirements.txt). Hooks will run on the current commit snapshot when executing a `git commit`. To install the hooks, run the following command: `python -m pre_commit install --install-hooks`

### Contributing

The following steps assume you have already completed all [setup](#setup) procedures.

> [!IMPORTANT]
> You do not need to render this project prior to committing changes to GitHub. The [GitHub Actions workflow](./.github/workflows/pubish.yaml) will automatically render the site when changes are pushed to the repository.

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
7. Once finished, render the site to verify it renders correctly (this may take a couple minutes): `quarto render`

   **Or**, target specific sections or pages to render instead of the entire site such as `quarto render docs/data-management` or `quarto render docs/data-management/index.qmd`.

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

## GitHub Actions

This repository uses a [self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) to render the site and publish it to GitHub Pages. The workflow is defined in the [publish.yaml](./.github/workflows/publish.yaml) file.

The runner is hosted on the `posit` machine (`192.168.0.10`) and is managed by Caleb Grant (`/home/cgrant/GitHub/actions-runner`). The runner is configured to run as a service and is started automatically when the machine boots up.

This repository uses a self-hosted runner due to the need for various resources only available on the `posit` machine. The runner is configured to run on the `main` branch pushes only.

### Configure the Runner

1. In the GitHub repository, navigate to `Settings` > `Actions` > `Runners`
2. Click the `New self-hosted runner` button
3. For the runner image, select `Linux`.
4. For the architecture, select `x64`.
5. On the posit machine, login as `cgrant` and navigate to `/home/cgrant@gsi-pc.local/GitHub`
6. Follow the instructions on GitHub to configure the runner (also outlined below)
7. Create the `actions-runner` directory:

   ```sh
   mkdir actions-runner && cd actions-runner
   ```

8. Download the latest runner package:

   ```sh
   curl -o actions-runner-linux-x64-2.321.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
   ```

9. Extract the installer:

   ```sh
   tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz
   ```

10. Create the runner and start the configuration process. Accept all the defaults.

    ```sh
    ./config.sh --url https://github.com/GSIEnvironmental/Phytoplankton_Indicator_Phase2 --token <REG_TOKEN>
    ```

11. Install the runner as a service:

    ```sh
    sudo ./svc.sh install
    ```

12. Start the runner service:

    ```sh
    sudo ./svc.sh start
    ```

13. Verify the runner is running:

    ```sh
    sudo ./svc.sh status
    ```

    > To stop the service, run `sudo ./svc.sh stop`

14. The runner should now be available in the GitHub repository under `Settings` > `Actions` > `Runners`
