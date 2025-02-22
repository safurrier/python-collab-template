![Tests](https://github.com/eugeneyan/python-collab-template/workflows/Tests/badge.svg) [![codecov](https://codecov.io/gh/eugeneyan/python-collab-template/branch/master/graph/badge.svg)](https://codecov.io/gh/eugeneyan/python-collab-template)

# Python Project Template

A modern Python project template with best practices for development and collaboration.

## Features
- 🚀 Fast dependency management with [uv](https://github.com/astral-sh/uv)
- ✨ Code formatting with [ruff](https://github.com/astral-sh/ruff)
- 🔍 Type checking with [mypy](https://github.com/python/mypy)
- 🧪 Testing with [pytest](https://github.com/pytest-dev/pytest)
- 🐳 Docker support for development and deployment
- 👷 CI/CD with GitHub Actions

## Quickstart
```bash
# Clone this repo and change directory
git clone git@github.com:eugeneyan/python-collab-template.git
cd python-collab-template

# Install dependencies and set up the environment
make setup

# Run the suite of tests and checks
make check

# Optional: Remove example code to start fresh
make clean-example
```

## Development Commands

### Quality Checks
```bash
make check      # Run all checks (test, mypy, lint, format)
make test       # Run tests with coverage
make mypy       # Run type checking
make lint       # Run linter
make format     # Run code formatter
```

### Example Code
The repository includes a simple example showing:
- Type hints
- Dataclasses
- Unit tests
- Modern Python practices

To remove the example code and start fresh:
```bash
make clean-example
```
## Docker Support

### Development Environment
```bash
make dev-env    # Start a development container
```

This creates a container with:
- All dependencies installed
- Source code mounted (changes reflect immediately)
- Development tools ready to use

### Production Image
```bash
make build-image    # Build production image
make push-image     # Push to container registry
```

## Project Structure
```
.
├── src/                # Source code
├── tests/             # Test files
├── docker/            # Docker configuration
├── .github/           # GitHub Actions workflows
├── pyproject.toml     # Project configuration
└── Makefile          # Development commands
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure all tests pass
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
