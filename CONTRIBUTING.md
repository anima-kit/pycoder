# 🔗 Contributing

I welcome contributions from the community, whether you're fixing bugs, improving documentation, adding features, or enhancing performance. Before submitting a pull request, please review the guidelines below to ensure a smooth process.

> 🛡️ **Security Policy**: If you discover any security vulnerabilities, please follow the instructions in our [Security Policy][security] and report them privately via GitHub's Private Vulnerability Reporting feature. Do not open issues or PRs for security concerns.

I also ask that all contributors follow the [Code of Conduct][conduct-code].

---

## Guidelines

1. **Opening Issues**

   - If you've found a bug or want to suggest an improvement, open an issue in the [issue tracker][issues].
   - Search existing issues to avoid duplicates.
   - Include detailed steps to reproduce bugs (if applicable) and any relevant logs or error messages.
2. **Submitting Pull Requests**

   - Fork the repository and create a new branch for your work.
   - Reference related issues in your PR description.
   - Keep commits small and focused on a single purpose.
   - Write clear, descriptive commit messages.

## Communication, Testing, Documentation

- First, discuss major changes in an issue before submitting PRs.
- Then, ensure all code changes are tested locally. If applicable, add or update tests for new features.
- Finally, update documentation to reflect changes. For major features, include usage examples or configuration details.

---

## Code Quality Standards

### General Code Quality

- Follow the existing code style and conventions in the project.
- Write clean, readable, and maintainable code.
- Avoid code duplication; favor reusability and modularity.
- Include meaningful comments for complex logic.

### Documentation Requirements

- Update README with any new features or configuration options.
- Add inline documentation for all added features.
- Include usage examples for new functionality.
- Ensure all configuration options are documented.

---

## Testing Requirements

### Test Coverage

- All new features must include corresponding unit tests.
- Integration tests should be added for complex workflows or system interactions.

### Testing Standards

- Tests must pass before submitting a PR.
- Follow the existing testing framework and patterns in the project.
- Use descriptive test names that clearly indicate what's being tested.
- Ensure tests are isolated and don't have side effects.
- Maintain consistent test structure and naming conventions.

### Running Tests

- Run all existing tests locally before submitting your PR.
- Include test results or verification steps in your PR description when relevant.
- For projects with multiple services, ensure integration tests cover the complete flow.

---

## Code Review Process

- All PRs require at least one review from maintainers.
- Address all feedback and make necessary changes.
- Squash commits if needed for a cleaner history.

---

## Example Workflow for New Contributors

1. Fork the repository
2. Clone locally: `git clone https://github.com/anima-kit/pycoder.git`
3. Create a branch: `git checkout -b feature/new-feature`
4. Make your changes
5. Run tests locally: `pytest tests/`
6. Commit with clear message: `git commit -m "Add user login functionality"`
7. Push to your fork: `git push origin feature/new-feature`
8. Open PR in GitHub

---

## Licensing

- Your contributions will be licensed under the project's [License][license]. By submitting a PR, you agree to this license.
- If adding third-party code or dependencies, ensure they are compatible with the project's licensing.

---

Thanks for contributing!

[conduct-code]: CODE_OF_CONDUCT.md
[issues]: https://github.com/anima-kit/pycoder/issues
[license]: LICENSE
[security]: SECURITY.md
