# Contributing to GoPro Plus Downloader

Thank you for your interest in contributing! This document provides guidelines for developers who want to contribute to the project.

## 🛠️ Development Setup

### Prerequisites

Before you can develop locally, you need to have the following installed:

* `python3.10+`
* `pip3`
* `direnv` (*optional*)
* `docker` (*optional*)

### Local Installation

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/maxrodrigo/gopro-plus.git
   cd gopro-plus
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. (*Optional*) Set up direnv for automatic environment activation:
   ```bash
   echo "source .venv/bin/activate" > .envrc
   echo "export AUTH_TOKEN='<your-token>'" >> .envrc
   echo "export USER_ID='<your-user-id>'" >> .envrc
   direnv allow
   ```

### Running Locally

Basic usage:
```bash
./gopro
```

Available command-line options:

* `--action <list|download>` - Action to execute (default: `download`)
* `--start-page <number>` - Start from a specific page (default: `1`)
* `--pages <number>` - Number of pages to process (default: all pages)
* `--per-page <number>` - Items per page (default: `30`)
* `--download-path <path>` - Directory to store downloaded files (default: `./download`)
* `--progress-mode <inline|newline|noline>` - Download progress display mode (default: `inline`)
* `--max-retries <number>` - Maximum retry attempts for failed downloads (default: `5`)

Examples:
```bash
# List all media without downloading
./gopro --action list

# Download to a specific directory
./gopro --download-path /path/to/storage

# Download pages 5-10 with 50 items per page
./gopro --start-page 5 --pages 6 --per-page 50

# Download with verbose progress output
./gopro --progress-mode newline
```

## 🐳 Docker Development

### Makefile Commands

The project includes a `Makefile` with convenient shortcuts:

* `make build` - Build a Docker container
* `make release` - Build and release the Docker image for multiple platforms
* `make run` - Run as local Docker container
* `make stop` - Stop Docker container
* `make logs` - Show Docker logs in follow mode
* `make clean` - Stop and remove spawned containers

### Dockerfile

The `Dockerfile` contains the base configuration for the Docker image.

## 📝 Coding Guidelines

* Follow Python best practices and PEP 8 style guide
* Write clear, descriptive commit messages using conventional commits format:
  - `feat:` - New features
  - `fix:` - Bug fixes
  - `docs:` - Documentation changes
  - `refactor:` - Code refactoring
  - `test:` - Adding or updating tests
* Keep changes focused and atomic
* Test your changes thoroughly before submitting

## 🔄 Contribution Workflow

1. **Fork** the repository
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Make your changes** and commit them:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
4. **Push** to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```
5. **Open a Pull Request** with a clear description of your changes

## 🐛 Reporting Issues

When reporting issues, please include:

* Clear description of the problem
* Steps to reproduce
* Expected vs actual behavior
* Environment details (OS, Python version, Docker version if applicable)
* Relevant logs or error messages

## 💡 Feature Requests

Feature requests are welcome! Please open an issue describing:

* The problem you're trying to solve
* Your proposed solution
* Any alternatives you've considered

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
