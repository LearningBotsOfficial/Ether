# Contributing to Ether

First off, thank you for considering contributing to Ether! It's people like you that make Ether such a powerful and versatile Telegram framework.

## Code of Conduct

By participating in this project, you agree to abide by our community standards:
*   Be respectful and inclusive.
*   Focus on technical excellence and clean code.
*   Respect the project's licensing and attribution terms.

## How Can I Contribute?

### 1. Developing Plugins
Ether is designed to be modular. The best way to contribute is by building new plugins.
*   Create a new `.py` file in the `plugins/` directory.
*   Ensure every plugin has a `setup(ether, db, owner_id)` function.
*   Follow the existing plugin patterns for consistency.

### 2. Core Improvements
If you want to modify the core architecture:
*   **Fork** the repository.
*   Create a **Feature Branch** (`git checkout -b feature/amazing-feature`).
*   Keep your changes atomic and well-documented.

### 3. Reporting Bugs
*   Check the [Issues](https://github.com/LearningBotsOfficial/Ether/issues) to see if it's already been reported.
*   Provide a clear description of the bug, including steps to reproduce and logs if possible.

## Coding Standards

To maintain a professional codebase, please follow these guidelines:

*   **PEP 8**: Follow standard Python styling.
*   **Typing**: Use Python type hints where possible for better IDE support.
*   **Documentation**: Add docstrings to complex functions and comments for non-obvious logic.
*   **Logging**: Use the built-in `get_logger` for all console and file output. Avoid `print()` statements in production code.

## Attribution Policy

Ether is a Source-Available project. 
*   **Do Not Remove Credits**: Any contribution that attempts to remove or obscure the original credits to LearningBotsOfficial will be rejected.
*   **Respect the MIT License**: Ensure any third-party code you include is compatible with our license.

## Pull Request Process

1.  Update the `README.md` if your change adds new functionality or configuration variables.
2.  Ensure your code passes basic linting and testing.
3.  Submit your PR with a descriptive title and a summary of the changes.

---

**Made with love by [LearningBotsOfficial](https://github.com/LearningBotsOfficial)**
