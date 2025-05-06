"""Command-line interface for TheDoc."""

import click

@click.group()
def main():
    """TheDoc - Documentation generation tool."""
    pass

@main.command()
def init():
    """Initialize TheDoc in the current project."""
    click.echo("Initializing TheDoc...")

@main.command()
def generate():
    """Generate documentation for the project."""
    click.echo("Generating documentation...")

@main.command()
def release_notes():
    """Generate release notes based on conventional commits."""
    click.echo("Generating release notes...")

@main.command()
def build():
    """Build MkDocs documentation site."""
    click.echo("Building documentation site...")

if __name__ == "__main__":
    main() 