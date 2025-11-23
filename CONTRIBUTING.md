# How to contribute to pyserde

Thank you for considering contributing to pyserde!

## Reporting issues
- Describe what you expected to happen.
- If possible, include a [minimal reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) to help us identify the issue. This also helps check that the issue is not with your own code.
- Describe what actually happened. Include the full traceback if there was an exception.
- List your Python and pyserde versions. If possible, check if this issue is already fixed in the repository.

## Submitting patches
- pyserde uses [black](https://github.com/psf/black) to autoformat your code. This should be done for you as a git pre-commit hook, which gets installed when you run `make setup` but you can do it manually via `make fmt` or `make check`.
- Include tests if your patch is supposed to solve a bug, and explain clearly under which circumstances the bug happens. Make sure the test fails without your patch.
- Include a string like “Fixes #123” in your commit message (where 123 is the issue you fixed). See [Closing issues using keywords](https://help.github.com/articles/creating-a-pull-request/).

### First time setup
- Download and install the latest version of [git](https://git-scm.com/downloads).
- Configure git with your [username](https://help.github.com/articles/setting-your-username-in-git/) and [email](https://help.github.com/articles/setting-your-email-in-git/):
  ```bash
  git config --global user.name 'your name'
  git config --global user.email 'your email'
  ```
- Make sure you have a [GitHub account](https://github.com/join).
- Fork pyserde to your GitHub account by clicking the [Fork](https://github.com/yukinarit/pyserde/fork) button.
- [Clone](https://help.github.com/en/articles/fork-a-repo#step-2-create-a-local-clone-of-your-fork) your GitHub fork locally:
  ```bash
  git clone https://github.com/{your-github-username}/pyserde
  cd pyserde
  ```
- Add the main repository as a remote to update later:
  ```bash
  git remote add upstream https://github.com/yukinarit/pyserde
  git fetch upstream
  ```
- Install [uv](https://github.com/astral-sh/uv) (used for dependency management and packaging). You can follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/) or run:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Run setup script:
  ```bash
  make setup
  ```

### Start coding
- Create a branch to identify the issue you would like to work on:
  ```bash
  git checkout -b your-branch-name origin/main
  ```
- Using your favorite editor, make your changes, committing as you go.
- Include tests that cover any code changes you make. Make sure the test fails without your patch. Run the tests via `make test`.
- Push your commits to GitHub and [create a pull request](https://help.github.com/en/articles/creating-a-pull-request) by using:
  ```bash
  git push --set-upstream origin your-branch-name
  ```

### Linters & Type checkers
pyserde uses the following tools. mypy and pyright are enabled for `/examples` directory at the moment.
* black
* pyright
* ruff
* mypy

If pre-commit is configured, `black`, `pyright` and `ruff` are automatically triggered when making a git commit. If you want to run mypy, run
```
make check  # this also runs black, pyright and ruff
```
or
```
mypy .
```
