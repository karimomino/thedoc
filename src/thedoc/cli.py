"""Command-line interface for TheDoc."""

import click
from pathlib import Path

from .mkdocs_generator import MkDocsGenerator
from .config import load_config, save_config, DEFAULT_CONFIG

@click.group()
def main():
    """TheDoc - Documentation generation tool."""
    pass

@main.command()
def init():
    """Initialize TheDoc in the current project."""
    click.echo("Initializing TheDoc...")
    
    project_name = click.prompt("Project name", default="")
    
    config = DEFAULT_CONFIG.copy()
    config["project_name"] = project_name
    
    save_config(config)
    
    click.echo("TheDoc initialized successfully.")

@main.command()
def generate():
    """Generate documentation for the project."""
    click.echo("Generating documentation...")
    
    project_path = Path.cwd()
    
    generator = MkDocsGenerator(project_path)
    
    generator.generate()

@main.command()
def release_notes():
    """Generate release notes based on conventional commits."""
    click.echo("Generating release notes...")
    # TODO: Implement release notes generation

@main.command()
def build():
    """Build MkDocs documentation site."""
    click.echo("Building documentation site...")
    
    config = load_config()
    docs_dir = Path.cwd() / config["output_dir"]
    
    if not docs_dir.exists():
        click.echo(f"Documentation directory not found: {docs_dir}")
        click.echo("Run 'thedoc generate' first to generate documentation.")
        return
    
    import subprocess
    try:
        subprocess.run(["mkdocs", "build"], cwd=docs_dir, check=True)
        click.echo(f"Documentation site built successfully in {docs_dir}/site")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error building documentation site: {e}")
    except FileNotFoundError:
        click.echo("MkDocs not found. Install it with 'pip install mkdocs mkdocs-material'.")

@main.command()
def serve():
    """Start the MkDocs development server."""
    click.echo("Starting documentation server...")
    
    config = load_config()
    docs_dir = Path.cwd() / config["output_dir"]
    
    if not docs_dir.exists():
        click.echo(f"Documentation directory not found: {docs_dir}")
        click.echo("Run 'thedoc generate' first to generate documentation.")
        return
    
    import subprocess
    try:
        subprocess.run(["mkdocs", "serve"], cwd=docs_dir, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error serving documentation site: {e}")
    except FileNotFoundError:
        click.echo("MkDocs not found. Install it with 'pip install mkdocs mkdocs-material'.")

if __name__ == "__main__":
    main() 