# Contributing

Welcome ! Thank you in advance for your contribution to Napse !

There are several ways in which you can contribute, beyond writing code. The goal of this document is to provide a high-level overview of how you can get involved.

## Questions & Feedbacks

Have a question ? Want to give a feedback ? Instead of opening an issue, please use the [discussion](https://github.com/napse-invest/django-napse/discussions) section.

## Basics

For small changes (e.g., bug fixes, documentation improvement), feel free to submit a PR.
For larger changes (e.g., new feature), please open an issue first to discuss the proposed changes.

!!! warning
    For your pull requests, please respect the linter ruff rules and tests your code (see [Code contribution](#code-contribution) section), otherwise, you'll be automatically rejected.

### Issues

Have you identified a reproducible problem in django-napse? Do you have a feature request? You can help us to progress and to become the best open source investment platform.
Before you create a new issue, please do a search in [open issues](https://github.com/napse-invest/django-napse/issues) to see if the issue or feature request has already been filed.

If you open a new issue for a bug report or a feature request, please read the following guidelines to write a good issue / feature request:
=== "Bug report"

    - A issue per bug report. Do not report several bugs in one issue.
    - Give all informations you can provide to make the problem reproducible and allow us to fix it.
    - You can add screenshots to illustrate the problem.

=== "Feature request"

    - A issue per feature requets. Do not request several features requests in one issue.
    - All feature request must answer to this two questions: **Why** and **How**.


## Setup development environnement

If you would like to go a steup further and write some code to contributing, we would love to hear from you! 

The first step is to setting up the development environnement to run the project on your local machine.

### Prerequisites

You will need the following tools:

- [Git](https://git-scm.com/)
- `make` ([make for windows](https://linuxhint.com/install-use-make-windows/))
- [Python](https://www.python.org/downloads/) `>=3.11`
- [Ruff](https://docs.astral.sh/ruff/) `>=1.3`


#### Clone the project from github

First fork the repository, then clone it to your local machine:
```bash
git clone https://github.com/<your-github-account>/django-napse.git
```

You can commit the code from your fork through a pull request on the official repository.

#### Build the virtual environment:

=== "Linux"

    ```bash
    source setup/setup-unix.sh
    ```

=== "MacOS"

    ```bash
    source setup/setup-osx.sh
    ```

=== "Windows"

    ```powershell
    .\setup\setup-windows.ps1
    ```

#### Setup initial exchange accounts

To make full use of the project, we recommend that you fill in the API keys of at least one exchange (among the django-napse [compabile exchanges](#compatible-exchanges)).

At `tests/test_app/`, build a `secret.json` file (or run the `./setup_secrets.sh` script). Here is an exemple with Binance:
```json
{
    "Exchange Accounts": {
        "Binance EA_NAME": {
            "exchange": "BINANCE",     # Name of your exchange (BINANCE, DYDX, ...)
            "testing": true,
            "public_key": "YOUR_PUBLIC_KEY",
            "private_key": "YOUR_PRIVATE_KEY"
        }
    }
}
```

!!! note
    We **strongly recommend** to add the `secret.json` file to your `.gitignore` file to avoid sharing your API keys.

#### Run 

```bash
make makemigrations
make migrate
make runserver
```

### Project structure

The project contains 5 parts:
```
.
├─ django_napse/
│  └─ api/
│  └─ auth/
│  └─ core/
│  └─ simulations/
│  └─ utils/
```

- `api`: Serialize data from database and allows interaction with models via endpoints.
- `auth`: Contains stuff for authorizations keys
- `core`: The heart of the project, contains all the logic within the django's models
- `simulations`: The environment to allow backtest on bots
- `utils`: Several usefull tools



## Documentation

In order to produce the best possible documentation, it is based on the [diataxis](https://diataxis.fr/) framework. 

Feel free to request the addition of a **tutorial**, a **how-to guide** or an **explanation** by means of a pull request or a simple issue with the `documentation` tag.
The **reference** section is generated automatically from docs strings in the code.
If you find an error or something missing, don't hesitate to open an issue or a pull request.

### Mkdocs

This documentation is build with [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/). 
To preview any changes to the documentation locally:
```bash
make mkdocs
```
The documentation should then be available locally at http://localhost:8005/.

## Code contribution

The code you contribute to the project must follow a standard. This standard ensures that all code is consistent, thant it has a certain quality and, above all, makes it easier for the various contributors to handle it.

### Code quality

To ensure a certain code quality, we use Ruff as a linter.
This is configured using `pyproject.toml`, which is at the root of the repository.
To install and use ruff, please follow the [official documentation](https://docs.astral.sh/ruff/tutorial/).

We strongly recommand to use a formatter to format your code. You can use both ruff formatter or black formatter.

??? tip Use ruff

    Use ruff linter:
    ```bash
    ruff check .
    ```

    Use ruff formatter:
    ```bash
    ruff format .
    ```

### Tests

⚠️ Work in progress ⚠️