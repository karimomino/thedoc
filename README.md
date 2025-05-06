# TheDoc

A powerful documentation generation tool that works with any programming language. TheDoc automatically generates comprehensive documentation and release notes based on conventional commits, with seamless MkDocs integration for beautiful web documentation.

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