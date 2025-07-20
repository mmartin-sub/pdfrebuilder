# Contributing to the Project

Thank you for your interest in contributing to this project! We welcome all contributions, from bug fixes to new features.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

3. **Set up the development environment** by following the instructions in our technical documentation: [.kiro/steering/tech.md](.kiro/steering/tech.md).

## Development Workflow

1. **Create a new branch** for your changes:

    ```bash
    git checkout -b my-feature-branch
    ```

2. **Make your changes** to the codebase.
3. **Ensure all tests pass**:

    ```bash
    hatch run test
    ```

4. **Run the pre-commit hooks** to format and lint your code:

    ```bash
    pre-commit run --all-files
    ```

5. **Commit your changes** with a clear and descriptive commit message:

    ```bash
    git commit -m "feat: Add new feature"
    ```

6. **Push your changes** to your fork:

    ```bash
    git push origin my-feature-branch
    ```

7. **Open a pull request** on the main repository's `main` branch.

## Pull Request Guidelines

- Please provide a clear and descriptive title and description for your pull request.
- Explain the changes you have made and why you have made them.
- If your pull request addresses an existing issue, please link to it.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
