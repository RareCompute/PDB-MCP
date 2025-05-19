
# Context Summary

*Purpose*: Hold all GitHub-specific automation and community files so the repository builds, tests, scans, and releases itself without manual intervention. Everything here affects how GitHub reacts to pushes, pull-requests, security reports, and dependency updates.
*Interacts with*: Actions Runners (CI), Docker Hub/GHCR (image publish, optional), project root badges in README.md, and every source sub-tree that the CI lints, tests, or packages.
*Key features / constraints*:
    1. CI Pipeline must mirror local dev commands (lint → pytest → Docker build).
    2. Workflows should run on Ubuntu-latest, Python 3.11.
    3. No hard-coded secrets—use GitHub Secrets for anything sensitive.
    4. Badge URLs must reference workflow file names exactly.
    5. All workflow steps must exit non-zero on failure to satisfy BUILD_PLAN checkpoints.
*Relevant external dirs*: tests/ (run by CI), Dockerfile (built by CI), any future docs/ for release notes.

## Key Files and Their Roles

This table outlines the primary files and directories within `.github` and their responsibilities:

| File / Directory                        | Responsibility                                                                                                    |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `workflows/`                            | Contains GitHub Actions workflow configurations.                                                                  |
|   └─ `workflows/ci.yml`                 | Defines the Continuous Integration (CI) pipeline: lints, tests, and builds the Docker image on every push/PR.     |
|   └─ `workflows/README.md`              | Provides a context summary specifically for the `workflows` directory and its contents.                           |
| `ISSUE_TEMPLATE/`                       | Contains templates for creating GitHub issues.                                                                    |
|   └─ `ISSUE_TEMPLATE/bug_report.md`     | Pre-filled form for reporting bugs, guiding users to provide reproducible steps and environment information.      |
|   └─ `ISSUE_TEMPLATE/feature_request.md`| Pre-filled form for proposing enhancements, helping users capture use-cases and acceptance criteria.              |
|   └─ `ISSUE_TEMPLATE/README.md`         | (Recommended) Provides a context summary for issue templates.                                                     |
| `pull_request_template.md`              | A checklist displayed when creating pull requests, reminding contributors to link issues, run tests, and update docs. |
| `dependabot.yml`                        | Configures Dependabot for automated weekly PRs to update Python packages and workflow actions to their latest secure versions. |
| `SECURITY.md`                           | Outlines the security policy, including how to privately report vulnerabilities and expected patch timelines.       |
| `README.md`                             | This file: Provides a high-level overview of the `.github` directory's purpose and contents.                     |
