# Contributing to WhisperTron

First off, thank you for considering contributing to WhisperTron! It's people like you that make WhisperTron such a great tool.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

## Code of Conduct

This project and everyone participating in it is governed by the WhisperTron Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [drew@drewburchfield.com](mailto:drew@drewburchfield.com).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for WhisperTron. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**

* Check the [issues](https://github.com/your-username/whispertron/issues) for a list of current known issues.
* Perform a [cursory search](https://github.com/your-username/whispertron/issues) to see if the problem has already been reported. If it has and the issue is still open, add a comment to the existing issue instead of opening a new one.

**How Do I Submit A (Good) Bug Report?**

Bugs are tracked as [GitHub issues](https://github.com/your-username/whispertron/issues). Create an issue and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem.
* **If the problem is related to performance or memory**, include a CPU profile capture with your report.
* **If the console shows any errors**, include the exact text in the report.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for WhisperTron, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion:**

* Check if the enhancement has already been suggested.
* Determine which repository the enhancement should be suggested in.
* Perform a [cursory search](https://github.com/your-username/whispertron/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

**How Do I Submit A (Good) Enhancement Suggestion?**

Enhancement suggestions are tracked as [GitHub issues](https://github.com/your-username/whispertron/issues). Create an issue and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Include screenshots and animated GIFs** which help you demonstrate the steps or point out the part of WhisperTron which the suggestion is related to.
* **Explain why this enhancement would be useful** to most WhisperTron users.
* **List some other applications where this enhancement exists.**

### Pull Requests

The process described here has several goals:

- Maintain WhisperTron's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible WhisperTron
- Enable a sustainable system for WhisperTron's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 🚱 `:non-potable_water:` when plugging memory leaks
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies

### Python Styleguide

* Follow [PEP 8](https://pep8.org/).
* Use 4 spaces for indentation (not tabs).
* Maximum line length of 100 characters.
* Use `snake_case` for functions and variables.
* Use `CamelCase` for classes.
* Use descriptive variable names.
* Include docstrings for all functions, classes, and modules.
* Write [good commit messages](https://chris.beams.io/posts/git-commit/).

### UI Development Styleguide

* Maintain consistency with existing UI elements
* Use Qt's layout managers instead of fixed positioning
* Test on different screen resolutions
* Consider accessibility
* Follow the platform's UI guidelines where appropriate

## Setting Up a Development Environment

### Prerequisites

* Python 3.11+
* FFmpeg
* Git
* Make (for building whisper.cpp)
* C++ compiler with C++11 support

### Setup

1. Fork the repository on GitHub.

2. Clone your fork locally:
   ```bash
   git clone git@github.com:your-username/whispertron.git
   cd whispertron
   ```

3. Set up the development environment:
   ```bash
   ./setup.sh
   ```

4. Create a branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. Make your changes

6. Push to your fork and submit a pull request.

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs.
* `documentation` - Issues or PRs related to documentation.
* `enhancement` - Issues that are feature requests or PRs that implement a new feature.
* `good first issue` - Good for newcomers.
* `help wanted` - Extra attention is needed.
* `invalid` - Issues that are invalid or non-actionable.
* `question` - Issues that are a question or require more information.
* `wontfix` - Issues that will not be worked on.

## Thank You!

Your contributions to open source, large or small, make projects like this possible. Thank you for taking the time to contribute. 