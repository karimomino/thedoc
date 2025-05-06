# TheDoc

[![PyPI version](https://badge.fury.io/py/thedoc.svg)](https://badge.fury.io/py/thedoc)
[![Development Status](https://img.shields.io/badge/status-alpha-yellow)](https://github.com/karimomino/thedoc)

> **🚧 WORK IN PROGRESS 🚧**  
> This project is currently under active development and is not yet feature-complete. Structure may change, features may be added or removed, and documentation may be incomplete. This will be worked on on my free time, so there are no clear timelines for anything.

A powerful documentation generation tool that works with most major programming language. TheDoc automatically generates comprehensive documentation and release notes based on conventional commits and doc comments, with seamless MkDocs integration for beautiful web documentation.

## Development Status

TheDoc is currently in the **alpha** stage. Core functionality works but more features are planned. See the [ROADMAP.md](ROADMAP.md) for details on planned features and improvements.

## Features

- Language-agnostic code analysis
- Automatic documentation generation
- Release notes generation from conventional commits
- MkDocs integration for web documentation
- Support for multiple programming languages
- Customizable documentation templates

## Installation

```bash
pip install thedoc
```

## Quick Start

1. Initialize TheDoc in your project:
```bash
thedoc init
```

2. Generate documentation:
```bash
thedoc generate
```

3. Generate release notes:
```bash
thedoc release-notes
```

4. Build MkDocs site:
```bash
thedoc build
```

5. Serve MkDocs site locally:
```bash
thedoc serve
```

## Supported Languages

TheDoc currently supports parsing documentation from:
- Python (docstrings)
- Swift (documentation comments)
- Kotlin (KDoc)
- .NET (XML documentation comments for C# and VB)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/karimomino/thedoc.git
cd thedoc

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
