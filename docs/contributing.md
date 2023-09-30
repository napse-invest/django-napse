# Contributing

Welcome ! Thank you in advance for your contribution to Napse !

## Basics

django-napse welcomes contributions in the form of Pull Requests or issues.

For small changes (e.g., bug fixes, documentation improvement), feel free to submit a PR.
For larger changes (e.g., new feature), please open an issue first to discuss the proposed changes.

!!! warning
    For your pull requests, please respect the linter ruff rules (see [code quality](#code-quality) section) and tests your code (seel [tests](#tests)), otherwise, you'll be automatically rejected.

### Prerequisites

The first step is to set up the development environment

- For **Linux**:
    ```bash
    source setup-unix.sh
    ```
- For **Windows**:
    ```powershell
    .\setup-windows.ps1
    ```

!!! advice
    If you're using **Windows**, for the rest of this guide (and for your own convenience), please install [make](https://linuxhint.com/install-use-make-windows/).

Then, you can run a test version of the project to work with:
```bash
make makemigrations
```
```bash
make migrate
```
```bash
make runserver
```

### Development
⚠️ Work in progress ⚠️
### Project structure
⚠️ Work in progress ⚠️

## Documentation

In order to produce the best possible documentation, it is based on the [diataxis](https://diataxis.fr/) framework. 

Feel free to request the addition of a **tutorial**, a **how-to guide** or an **explanation** by means of a pull request or a simple issue with the `documentation` tag.
The **reference** section is generated automatically from docs strings in the code.
If you find an error or something missing, don't hesitate to open an issue or a pull request.

## Code contribution

### Code quality

To ensure a certain code quality, we use Ruff as a linter.
This is configured using `pyproject.toml`, which is at the root of the repository.
To install and use ruff, please follow the [official documentation](https://docs.astral.sh/ruff/tutorial/).


### Tests

⚠️ Work in progress ⚠️