# GitHub Workflows

This directory contains configurations for GitHub Actions workflows, which automate various aspects of the PDB-MCP project's development lifecycle.

## `ci.yml` - Continuous Integration

This workflow defines the Continuous Integration (CI) pipeline for the project. Its primary responsibilities are to ensure code quality, correctness, and style consistency automatically on every push and pull request to the `main` branch.

### Key Features

- **Triggered Events**: Runs automatically on `push` and `pull_request` events targeting the `main` branch.
- **Environment**: Executes on an `ubuntu-latest` runner with Python `3.11`.
- **Dependency Management**: Installs project dependencies from `requirements.txt`.
- **Linting**: Uses `black --check .` to verify code formatting and `flake8 .` for general Python linting to catch style issues and potential errors.
- **Testing**: Executes the test suite using `pytest -q`. This includes unit, integration, and any other tests defined in the `/tests` directory.

### Purpose

The `ci.yml` workflow acts as a crucial gatekeeper, helping to:

- Maintain a high standard of code quality throughout the project.
- Prevent regressions by ensuring all tests pass before code is merged.
- Provide rapid feedback to contributors on the status of their changes.
- Automate repetitive tasks, allowing developers to focus on building features.

This workflow is essential for the project's stability and adherence to the development practices outlined in the main `BUILD_PLAN.md` and repository READMEs.
