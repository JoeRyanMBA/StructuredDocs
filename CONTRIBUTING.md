# Contributing to StructuredDocs

Thank you for your interest in contributing! Here's how to get involved.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Follow the [Local Development](README.md#local-development-without-docker) setup in the README.
3. Create a feature branch: `git checkout -b feat/your-feature-name`

## Development Workflow

- Keep changes focused — one logical change per PR.
- Write or update tests for any new behaviour.
- Run the test suite before submitting:
  ```bash
  python -m pytest test_hierarchical_parsing_logic.py  # unit tests
  python -m pytest test_integration.py                 # integration tests (requires backend on :5050)
  ```
- Run the frontend linter:
  ```bash
  cd frontend && npm run lint
  ```

## Submitting a Pull Request

1. Push your branch to your fork and open a PR against `main`.
2. Fill in the PR template (description, motivation, testing steps).
3. Link any related issues with `Closes #<issue>`.
4. A maintainer will review and may request changes before merging.

## Reporting Bugs

Open a [GitHub Issue](https://github.com/JoeRyanMBA/StructuredDocs/issues) with:
- A clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behaviour
- Your environment (OS, Python version, browser)

## Requesting Features

Open an issue with the label `enhancement`. Describe the use case and proposed solution.

## Code Style

- **Python**: follow PEP 8; use `current_app.logger` for logging (not `print`).
- **Vue/JS**: follow the existing component structure in `frontend/src/`.
- **SQL migrations**: always add `server_default` to new columns so existing rows aren't broken.

## Security Vulnerabilities

Please **do not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
