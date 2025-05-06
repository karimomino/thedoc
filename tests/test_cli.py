"""Tests for the CLI module."""

from click.testing import CliRunner
from thedoc.cli import main

def test_main_command():
    """Test that the main command runs without error."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0

def test_init_command():
    """Test the init command."""
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "Initializing TheDoc" in result.output

def test_generate_command():
    """Test the generate command."""
    runner = CliRunner()
    result = runner.invoke(main, ["generate"])
    assert result.exit_code == 0
    assert "Generating documentation" in result.output 